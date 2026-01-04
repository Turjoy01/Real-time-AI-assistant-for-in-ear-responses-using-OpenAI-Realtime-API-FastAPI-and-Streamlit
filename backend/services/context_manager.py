from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContextManager:
    """
    Manages user-uploaded context for better AI responses.
    Stores and retrieves relevant information.
    """
    
    def __init__(self):
        self.contexts: List[Dict] = []
        self.max_context_length = 2000  # characters
        
    def add_context(self, content: str, source: str = "upload", metadata: dict = None):
        """Add new context with metadata"""
        context_entry = {
            'content': content[:self.max_context_length],
            'source': source,
            'timestamp': datetime.now(),
            'metadata': metadata or {},
            'word_count': len(content.split())
        }
        
        self.contexts.append(context_entry)
        logger.info(f"Added context from {source}: {len(content)} chars")
        
    def get_relevant_context(
        self,
        query: str = "",
        max_length: int = 500
    ) -> str:
        """
        Get relevant context for a query.
        Returns concatenated context up to max_length.
        """
        if not self.contexts:
            return ""
        
        # Simple strategy: return most recent context
        # In production, use semantic search (embeddings) for better relevance
        
        result = []
        total_length = 0
        
        for ctx in reversed(self.contexts):
            content = ctx['content']
            if total_length + len(content) <= max_length:
                result.insert(0, content)
                total_length += len(content)
            else:
                # Add partial content
                remaining = max_length - total_length
                if remaining > 100:  # Only add if meaningful amount
                    result.insert(0, content[:remaining])
                break
        
        return "\n\n".join(result)
    
    def search_context(self, keywords: List[str]) -> List[Dict]:
        """Search contexts by keywords"""
        results = []
        
        for ctx in self.contexts:
            content_lower = ctx['content'].lower()
            if any(keyword.lower() in content_lower for keyword in keywords):
                results.append(ctx)
        
        return results
    
    def clear_all(self):
        """Clear all contexts"""
        self.contexts = []
        logger.info("Cleared all contexts")
    
    def get_summary(self) -> Dict:
        """Get summary of stored contexts"""
        return {
            'total_contexts': len(self.contexts),
            'total_words': sum(ctx['word_count'] for ctx in self.contexts),
            'sources': list(set(ctx['source'] for ctx in self.contexts))
        }