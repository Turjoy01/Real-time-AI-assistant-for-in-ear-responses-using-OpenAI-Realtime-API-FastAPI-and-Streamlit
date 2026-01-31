from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import field_validator

class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 8501
    
    # CORS
    allowed_origins: Union[str, List[str]] = ["http://localhost:8501", "http://localhost:3000"]
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v
    
    # Audio
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # Question Detection
    confidence_threshold: float = 0.75
    min_question_length: int = 3
    
    # Response
    max_response_words: int = 15
    response_timeout: int = 5
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

settings = Settings()







































