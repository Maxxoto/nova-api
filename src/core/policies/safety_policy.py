"""Safety policy for agent actions and content validation."""

from typing import List, Dict, Any, Optional
from uuid import UUID

from ..entities.plan import Plan, PlanStep
from ..entities.agent_state import AgentState


class SafetyPolicy:
    """Safety policy implementation for agent actions and content."""
    
    def __init__(self):
        self.blocked_actions = [
            "delete_system_files",
            "modify_system_config",
            "access_sensitive_data",
            "execute_dangerous_commands"
        ]
        
        self.blocked_content_patterns = [
            "malicious_code",
            "sensitive_information",
            "harmful_instructions"
        ]
    
    def validate_action(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Validate if an action is safe to execute."""
        
        # Check for blocked actions
        if any(blocked in action.lower() for blocked in self.blocked_actions):
            return False
        
        # Validate parameters
        if not self._validate_parameters(parameters):
            return False
        
        return True
    
    def validate_content(self, content: str) -> bool:
        """Validate if content is safe."""
        
        # Check for blocked content patterns
        if any(pattern in content.lower() for pattern in self.blocked_content_patterns):
            return False
        
        # Additional content safety checks
        if self._contains_harmful_content(content):
            return False
        
        return True
    
    def validate_plan(self, plan: Plan, agent_state: AgentState) -> bool:
        """Validate if a complete plan is safe to execute."""
        
        # Check overall plan safety
        if not self._validate_plan_structure(plan):
            return False
        
        # Validate each step
        for step in plan.steps:
            if not self.validate_action(step.action, step.parameters):
                return False
        
        return True
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate action parameters for safety."""
        
        # Check for dangerous parameter values
        dangerous_values = ["rm -rf", "format", "delete_all"]
        for value in dangerous_values:
            if any(value in str(param).lower() for param in parameters.values()):
                return False
        
        return True
    
    def _contains_harmful_content(self, content: str) -> bool:
        """Check if content contains harmful instructions."""
        
        harmful_indicators = [
            "ignore safety",
            "bypass security",
            "override restrictions",
            "dangerous operation"
        ]
        
        return any(indicator in content.lower() for indicator in harmful_indicators)
    
    def _validate_plan_structure(self, plan: Plan) -> bool:
        """Validate the structure of a plan for safety."""
        
        # Check for infinite loops or dangerous sequences
        if len(plan.steps) > 100:  # Limit plan size
            return False
        
        # Check for dangerous step sequences
        dangerous_sequences = [
            ["access_data", "modify_data"],
            ["read_files", "delete_files"]
        ]
        
        step_actions = [step.action for step in plan.steps]
        for sequence in dangerous_sequences:
            if all(action in step_actions for action in sequence):
                return False
        
        return True