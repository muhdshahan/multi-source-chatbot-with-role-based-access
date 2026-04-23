"""
Query routing module for classifying user intent.
Determines which system component should handle the query.
"""

class QueryRouter:
    """Classifies queries into predefined categories."""
    
    def classify(self, query: str):
        """Return query type based on keyword matching."""
        query = query.lower()

        if "price" in query or "cost" in query:
            return "price"
        
        if "compare" in query:
            return "compare"
        
        if "list" in query or "under" in query:
            return "filter"
        
        video_keywords = [
            "person", "car", "bag", "backpack", "handbag",
            "traffic", "light", "signal", "find", "video", "frame"
        ]

        for word in video_keywords:
            if word in query:
                return "video"
        
        return "rag"