from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from datetime import datetime
from ..models import AIResponse, SystemStatus, ListeningStatus
from ..services.openai_service import OpenAIService
from ..services.context_manager import ContextManager
from ..services.question_detector import QuestionDetector
from ..services.speech_processor import SpeechProcessor
from ..config import settings
import time
import io

router = APIRouter()

# Services
openai_service = OpenAIService(api_key=settings.openai_api_key)
context_manager = ContextManager()
question_detector = QuestionDetector()
speech_processor = SpeechProcessor()

@router.post("/api/question", response_model=AIResponse)
async def process_question(question: str):
    """
    Process a direct question (for testing/debugging).
    In passive mode, this endpoint is rarely used.
    """
    start_time = time.time()
    
    # Check if it's actually a question
    is_question, confidence, q_type = question_detector.detect(question)
    
    if not is_question:
        return AIResponse(
            question=question,
            answer="Not a question",
            timestamp=datetime.now(),
            processing_time=0,
            spoken=False
        )
    
    # Get context and generate response
    context = context_manager.get_relevant_context(question)
    answer = await openai_service.generate_short_response(question, context)
    
    processing_time = time.time() - start_time
    
    return AIResponse(
        question=question,
        answer=answer,
        timestamp=datetime.now(),
        processing_time=processing_time,
        spoken=False
    )

@router.post("/api/voice")
async def process_voice(file: UploadFile = File(...)):
    """
    Process audio recording, transcribe, and detect questions.
    """
    start_time = time.time()
    try:
        audio_content = await file.read()
        
        # Transcribe
        text, confidence = speech_processor.process_audio_chunk(audio_content)
        
        if not text:
            return {"status": "no_speech", "message": "No speech detected"}
            
        # Filter noise
        if question_detector.filter_context_noise(text):
            return {"status": "noise", "transcription": text}
            
        # Detect question
        is_question, q_confidence, q_type = question_detector.detect(text)
        
        if not is_question:
            return {
                "status": "statement",
                "transcription": text,
                "confidence": q_confidence
            }
            
        # It's a question! Extract and respond
        actual_question = question_detector.extract_question(text)
        context = context_manager.get_relevant_context(actual_question)
        answer = await openai_service.generate_short_response(actual_question, context)
        
        processing_time = time.time() - start_time
        
        return {
            "status": "question_detected",
            "transcription": text,
            "extracted_question": actual_question,
            "answer": answer,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/context")
async def upload_context(file: UploadFile = File(...)):
    """Upload context file for better AI responses"""
    try:
        content = await file.read()
        text_content = content.decode('utf-8')
        
        context_manager.add_context(
            content=text_content,
            source=file.filename,
            metadata={'size': len(text_content)}
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(text_content),
            "summary": context_manager.get_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/api/context")
async def get_context_summary():
    """Get summary of uploaded contexts"""
    return context_manager.get_summary()

@router.delete("/api/context")
async def clear_contexts():
    """Clear all uploaded contexts"""
    context_manager.clear_all()
    return {"status": "success", "message": "All contexts cleared"}

@router.get("/api/history")
async def get_conversation_history():
    """Get conversation history"""
    return openai_service.conversation_context

@router.delete("/api/history")
async def clear_history():
    """Clear conversation history"""
    openai_service.clear_context()
    return {"status": "success", "message": "History cleared"}

@router.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status"""
    return SystemStatus(
        status=ListeningStatus.LISTENING,
        is_listening=True,
        transcription_active=True,
        question_detected=False,
        last_activity=datetime.now()
    )

@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": "passive_listening",
        "timestamp": datetime.now().isoformat()
    }