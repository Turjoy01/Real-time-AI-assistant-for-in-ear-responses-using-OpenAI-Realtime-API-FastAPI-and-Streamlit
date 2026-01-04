from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AudioChunk(BaseModel):
    audio_data: bytes
    timestamp: datetime
    
class TranscriptionResponse(BaseModel):
    text: str
    is_final: bool
    confidence: float
    timestamp: datetime

class QuestionDetection(BaseModel):
    text: str
    is_question: bool
    confidence: float
    question_type: Optional[str] = None

class AIResponse(BaseModel):
    question: str
    answer: str
    timestamp: datetime
    processing_time: float

class ContextData(BaseModel):
    content: str
    source: str
    timestamp: datetime

class ConversationEntry(BaseModel):
    question: str
    answer: str
    timestamp: datetime
    audio_url: Optional[str] = None