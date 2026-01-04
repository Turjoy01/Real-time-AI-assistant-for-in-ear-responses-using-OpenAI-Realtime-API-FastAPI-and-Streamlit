from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
import asyncio
from datetime import datetime
from ..services.openai_service import OpenAIService
from ..services.question_detector import QuestionDetector
from ..services.context_manager import ContextManager
from ..services.speech_processor import SpeechProcessor
from ..config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
openai_service = OpenAIService(api_key=settings.openai_api_key)
question_detector = QuestionDetector()
context_manager = ContextManager()
speech_processor = SpeechProcessor()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = {
            'socket': websocket,
            'status': 'listening',
            'last_activity': datetime.now()
        }
        logger.info(f"Client {client_id} connected - passive listening started")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id]['socket'].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for passive listening mode.
    AI remains silent, continuously monitoring for questions.
    """
    await manager.connect(client_id, websocket)
    
    # Send initial status
    await manager.send_message(client_id, {
        'type': 'status',
        'status': 'passive_listening',
        'message': 'AI is listening silently in the background'
    })
    
    try:
        while True:
            # Receive audio/transcription from client
            data = await websocket.receive_json()
            message_type = data.get('type')
            
            if message_type == 'audio_chunk':
                # Process audio (in production, this would be continuous)
                audio_data = data.get('audio')
                
                # Transcribe audio
                text, confidence = speech_processor.process_audio_chunk(audio_data)
                
                if text:
                    # Send transcription to client (for display only)
                    await manager.send_message(client_id, {
                        'type': 'transcription',
                        'text': text,
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Check if it's a question
                    await process_potential_question(client_id, text, confidence)
            
            elif message_type == 'transcription':
                # Direct transcription from client
                text = data.get('text', '')
                is_final = data.get('is_final', False)
                
                if is_final and text:
                    await process_potential_question(client_id, text, 0.85)
            
            elif message_type == 'context':
                # User uploaded context
                content = data.get('content', '')
                source = data.get('source', 'user_upload')
                context_manager.add_context(content, source)
                
                await manager.send_message(client_id, {
                    'type': 'context_updated',
                    'message': 'Context added',
                    'summary': context_manager.get_summary()
                })
            
            elif message_type == 'clear_history':
                # Clear conversation history
                openai_service.clear_context()
                context_manager.clear_all()
                
                await manager.send_message(client_id, {
                    'type': 'history_cleared',
                    'message': 'History and context cleared'
                })
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

async def process_potential_question(client_id: str, text: str, confidence: float):
    """
    Process text to detect questions and generate responses.
    Only responds when confident it's a direct question.
    """
    
    # Filter noise
    if question_detector.filter_context_noise(text):
        logger.debug(f"Filtered noise: {text}")
        return
    
    # Detect if it's a question
    is_question, q_confidence, q_type = question_detector.detect(text)
    
    # Send detection result to client
    await manager.send_message(client_id, {
        'type': 'question_detection',
        'text': text,
        'is_question': is_question,
        'confidence': q_confidence,
        'question_type': q_type
    })
    
    # Only respond if it's a confident question
    should_respond = (
        is_question and 
        q_confidence >= settings.confidence_threshold and
        len(text.split()) >= settings.min_question_length
    )
    
    if should_respond:
        logger.info(f"Question detected ({q_confidence:.2f}): {text}")
        
        # Notify client that AI is processing
        await manager.send_message(client_id, {
            'type': 'processing',
            'message': 'Generating response...'
        })
        
        # Get relevant context
        context = context_manager.get_relevant_context(text, max_length=500)
        
        # Generate AI response
        answer = await openai_service.generate_contextual_response(
            question=text,
            conversation_history=openai_service.conversation_context,
            user_context=context
        )
        
        # Store in conversation history
        openai_service.add_to_conversation(text, answer)
        
        # Send response to client
        await manager.send_message(client_id, {
            'type': 'ai_response',
            'question': text,
            'answer': answer,
            'confidence': q_confidence,
            'timestamp': datetime.now().isoformat(),
            'should_speak': True  # Trigger text-to-speech on client
        })
        
        logger.info(f"Responded: {answer}")
    else:
        logger.debug(f"No response needed for: {text}")