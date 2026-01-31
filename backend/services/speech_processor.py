import speech_recognition as sr
from typing import Optional, Tuple
import logging
import numpy as np
import io

logger = logging.getLogger(__name__)

class SpeechProcessor:
    """
    Handles real-time speech-to-text processing.
    Continuously listens and transcribes audio in the background.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Adjust based on environment
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence to consider end
        
    def process_audio_chunk(self, audio_data: bytes) -> Tuple[Optional[str], float]:
        """
        Process audio chunk (WAV bytes) and return transcription with confidence.
        Returns: (text, confidence)
        """
        try:
            # audio_data contains the full WAV file from the frontend
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio, show_all=False)
            
            # Estimate confidence
            confidence = 0.85
            
            logger.info(f"Successfully transcribed: \"{text}\"")
            return text, confidence
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None, 0.0
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return None, 0.0
        except Exception as e:
            logger.error(f"Speech processing error: {e}")
            return None, 0.0
    
    def listen_continuous(self, source):
        """
        Continuously listen to audio source.
        Yields audio chunks as they're detected.
        """
        with source as audio_source:
            self.recognizer.adjust_for_ambient_noise(audio_source, duration=1)
            
            while True:
                try:
                    # Listen for speech with timeout
                    audio = self.recognizer.listen(
                        audio_source,
                        timeout=None,
                        phrase_time_limit=10
                    )
                    yield audio
                    
                except Exception as e:
                    logger.error(f"Listening error: {e}")
                    continue
    
    def is_speech_detected(self, audio_data: np.ndarray) -> bool:
        """
        Simple voice activity detection (VAD).
        Returns True if speech-like audio is detected.
        """
        if audio_data.size == 0:
            return False
        # Calculate energy
        energy = np.abs(audio_data).mean()
        
        # Simple threshold-based detection
        return energy > 0.01



















        