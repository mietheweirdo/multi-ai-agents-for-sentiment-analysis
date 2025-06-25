"""
Prompt management module for multi-agent sentiment analysis system.
Organized similar to FinRobot structure for better maintainability.
"""

from .base_prompts import BasePrompts
from .agent_prompts import AgentPrompts
from .product_prompts import ProductPrompts
from .coordinator_prompts import CoordinatorPrompts

__all__ = [
    'BasePrompts',
    'AgentPrompts', 
    'ProductPrompts',
    'CoordinatorPrompts'
] 