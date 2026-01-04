from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ListeningStatus(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"

class AudioChunk(BaseModel):
    data: bytes
    timestamp: float
    duration: float

class TranscriptionResult(BaseModel):
    text: str
    confidence: float
    is_final: bool
    timestamp: datetime

class QuestionDetectionResult(BaseModel):
    text: str
    is_question: bool
    confidence: float
    question_type: Optional[str] = None
    should_respond: bool

class AIResponse(BaseModel):
    question: str
    answer: str
    timestamp: datetime
    processing_time: float
    spoken: bool = False

class ConversationEntry(BaseModel):
    speaker: str  # "user" or "ai"
    text: str
    timestamp: datetime
    is_question: bool = False

class SystemStatus(BaseModel):
    status: ListeningStatus
    is_listening: bool
    transcription_active: bool
    question_detected: bool
    last_activity: datetime