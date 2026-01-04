import asyncio
from openai import AsyncOpenAI
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Generates ultra-short AI responses for passive earbud assistance.
    Optimized for brevity and natural speech.
    """
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.conversation_context = []
        
    async def generate_short_response(
        self,
        question: str,
        context: str = "",
        max_words: int = 15
    ) -> str:
        """
        Generate an extremely short, natural response.
        Perfect for whispered earbud delivery.
        """
        start_time = time.time()
        
        try:
            # Ultra-concise system prompt
            system_prompt = (
                f"You're a helpful assistant whispering answers into someone's ear. "
                f"Give ONLY the direct answer in {max_words} words or less. "
                f"No explanations, no preamble, no punctuation at the end. "
                f"Just the essential information, like you're helping a friend cheat on a quiz."
            )
            
            # Build user prompt
            user_prompt = question
            if context:
                user_prompt = f"Context: {context[:200]}\n\nQuestion: {question}"
            
            # Call OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=30,  # Very short
                temperature=0.3,  # Low temp for consistency
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Enforce word limit strictly
            words = answer.split()
            if len(words) > max_words:
                answer = ' '.join(words[:max_words])
            
            # Remove trailing punctuation for natural speech
            answer = answer.rstrip('.,!?;:')
            
            # Log for debugging
            processing_time = time.time() - start_time
            logger.info(
                f"Generated response in {processing_time:.2f}s: "
                f"'{answer}' ({len(words)} words)"
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Sorry couldn't get that"
    
    async def generate_contextual_response(
        self,
        question: str,
        conversation_history: list,
        user_context: str = ""
    ) -> str:
        """
        Generate response with conversation history awareness.
        """
        # Build context from recent conversation
        recent_history = conversation_history[-5:]  # Last 5 exchanges
        context_text = "\n".join([
            f"Q: {entry['question']}\nA: {entry['answer']}"
            for entry in recent_history
        ])
        
        if user_context:
            context_text = f"{user_context}\n\n{context_text}"
        
        return await self.generate_short_response(
            question,
            context=context_text,
            max_words=15
        )
    
    def add_to_conversation(self, question: str, answer: str):
        """Store conversation for context awareness"""
        self.conversation_context.append({
            'question': question,
            'answer': answer,
            'timestamp': time.time()
        })
        
        # Keep only recent context (last 20 exchanges)
        if len(self.conversation_context) > 20:
            self.conversation_context = self.conversation_context[-20:]
    
    def clear_context(self):
        """Clear conversation context"""
        self.conversation_context = []