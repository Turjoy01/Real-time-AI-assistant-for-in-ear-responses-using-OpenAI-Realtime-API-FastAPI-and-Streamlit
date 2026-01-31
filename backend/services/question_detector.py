import re
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)

class QuestionDetector:
    """
    Highly aggressive question detector for passive earbud assistance.
    Designed to find questions within messy, unpunctuated speech-to-text.
    """
    
    def __init__(self):
        # Auxiliary verbs that start questions
        self.question_auxiliaries = [
            'is', 'are', 'was', 'were', 'do', 'does', 'did',
            'can', 'could', 'would', 'will', 'should', 'has', 'have'
        ]
        
        # Question words
        self.question_words = [
            'what', 'who', 'where', 'when', 'why', 'how', 'which'
        ]
        
        # Phrases that strongly indicate a question follows
        self.request_phrases = [
            'tell me', 'let me know', 'do you know', 'any idea',
            'wondering if', 'wondering about', 'do you think'
        ]

    def detect(self, text: str) -> Tuple[bool, float, str]:
        """
        Detect if text contains a question anywhere.
        Returns: (is_question, confidence, question_type)
        """
        if not text or len(text.strip()) < 5:
            return False, 0.0, 'none'
        
        text_clean = text.lower().strip()
        
        # 1. Check for explicit question mark
        if '?' in text:
            return True, 0.98, 'explicit_q'
            
        # 2. Check for "Do you think", "What is", etc. at the start of any segment
        # We split by common speech connectors
        segments = re.split(r'\b(also|and|so|but|then|hey|hello)\b', text_clean)
        
        for segment in segments:
            seg = segment.strip()
            if not seg: continue
            
            words = seg.split()
            if not words: continue
            
            # Check if segment starts with a question word or auxiliary
            if words[0] in self.question_words or words[0] in self.question_auxiliaries:
                if len(words) >= 3:
                    return True, 0.90, 'segment_start_q'
                    
        # 3. Aggressive Regex search for [Aux/Word] + [Pronoun/Subject]
        # Example patterns: "do you", "is it", "how can", "should i"
        pronouns = r'\b(you|i|we|it|they|he|she|this|that)\b'
        aux_pattern = r'\b(' + '|'.join(self.question_auxiliaries + self.question_words) + r')\b'
        
        # Pattern: [aux/word] followed immediately or shortly by a pronoun
        match = re.search(aux_pattern + r'\s+' + pronouns, text_clean)
        if match:
            # Check if it's "do you", "is it" etc.
            return True, 0.85, 'regex_pattern_q'
            
        # 4. Request phrases search
        for phrase in self.request_phrases:
            if phrase in text_clean:
                return True, 0.80, 'request_phrase_q'
                
        # 5. Fallback: Check for common question starters even if not at segment start
        # e.g., "... you think it is a good idea ..."
        if "you think" in text_clean or "your opinion" in text_clean:
            return True, 0.75, 'opinion_q'

        return False, 0.2, 'statement'

    def extract_question(self, text: str) -> str:
        """
        No-op for now - in continuous speech, usually better 
        to send the whole context to the LLM to decide.
        """
        return text

    def filter_context_noise(self, text: str) -> bool:
        """Filter out conversational filler."""
        fillers = [r'^um', r'^uh', r'^hmm', r'^ah', r'^oh', r'^well']
        text_lower = text.lower().strip()
        return any(re.match(f, text_lower) for f in fillers) and len(text_lower.split()) < 3
    






















































































































































    