from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

class EnhancedMemory:
    """Memory agent that maintains context and history for all agents."""
    
    def __init__(self, config=None):
        # Store config for future use if needed
        self.config = config or {}
        
        self.general_memory = ConversationBufferMemory(return_messages=True)
        self.product_insights = {}
        self.sentiment_history = {}
        
    def add_to_memory(self, role, content):
        """Add a new interaction to the general memory."""
        if role == "user":
            self.general_memory.chat_memory.add_user_message(content)
        elif role == "ai":
            self.general_memory.chat_memory.add_ai_message(content)
        elif role == "system":
            self.general_memory.chat_memory.messages.append(SystemMessage(content=content))
    
    def store_product_insight(self, product_id, insight):
        """Store insights about a specific product."""
        if product_id not in self.product_insights:
            self.product_insights[product_id] = []
        self.product_insights[product_id].append(insight)
    
    def store_sentiment_analysis(self, product_id, sentiment_data):
        """Store sentiment analysis results for a product."""
        if product_id not in self.sentiment_history:
            self.sentiment_history[product_id] = []
        self.sentiment_history[product_id].append(sentiment_data)
    
    def get_product_memory(self, product_id):
        """Get all stored information about a specific product."""
        return {
            "insights": self.product_insights.get(product_id, []),
            "sentiment_history": self.sentiment_history.get(product_id, [])
        }
    
    def get_chat_history(self):
        """Get the full conversation history."""
        return self.general_memory.chat_memory.messages
    
    def clear_memory(self):
        """Clear all stored memory."""
        self.general_memory = ConversationBufferMemory(return_messages=True)
        self.product_insights = {}
        self.sentiment_history = {}