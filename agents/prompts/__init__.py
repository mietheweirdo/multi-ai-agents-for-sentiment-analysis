"""
Prompt management module for multi-agent sentiment analysis system.
Organized for better maintainability and separation of concerns.
"""

from .base_prompts import BasePrompts
from .agent_prompts import AgentPrompts
from .product_prompts import ProductPrompts

__all__ = [
    'BasePrompts',
    'AgentPrompts', 
    'ProductPrompts'
] 