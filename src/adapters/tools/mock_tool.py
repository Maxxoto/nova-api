"""Mock tool adapter for testing and development."""

import asyncio
from typing import Dict, Any, List
from uuid import uuid4

from ...core.entities.plan import PlanStep
from ...core.entities.agent_state import AgentState


class MockToolAdapter:
    """Mock tool adapter for testing tool execution."""
    
    def __init__(self):
        self.available_tools = {
            "search_web": {
                "description": "Search the web for information",
                "parameters": {"query": "str"}
            },
            "read_file": {
                "description": "Read content from a file",
                "parameters": {"file_path": "str"}
            },
            "write_file": {
                "description": "Write content to a file",
                "parameters": {"file_path": "str", "content": "str"}
            },
            "execute_code": {
                "description": "Execute Python code",
                "parameters": {"code": "str"}
            },
            "send_email": {
                "description": "Send an email",
                "parameters": {"to": "str", "subject": "str", "body": "str"}
            }
        }
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a mock tool."""
        
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Mock tool execution results
        mock_results = {
            "search_web": {
                "success": True,
                "result": f"Mock search results for: {parameters.get('query', '')}",
                "execution_time": 0.1
            },
            "read_file": {
                "success": True,
                "result": f"Mock content from file: {parameters.get('file_path', '')}",
                "execution_time": 0.1
            },
            "write_file": {
                "success": True,
                "result": f"Successfully wrote to file: {parameters.get('file_path', '')}",
                "execution_time": 0.1
            },
            "execute_code": {
                "success": True,
                "result": "Code executed successfully (mock)",
                "execution_time": 0.1
            },
            "send_email": {
                "success": True,
                "result": f"Email sent to: {parameters.get('to', '')}",
                "execution_time": 0.1
            }
        }
        
        return mock_results.get(tool_name, {
            "success": False,
            "error": "Tool execution failed",
            "result": None
        })
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available mock tools."""
        
        tools = []
        for name, details in self.available_tools.items():
            tools.append({
                "name": name,
                "description": details["description"],
                "parameters": details["parameters"]
            })
        
        return tools
    
    async def validate_tool_usage(self, tool_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate if a tool can be used with given parameters."""
        
        if tool_name not in self.available_tools:
            return False
        
        tool_spec = self.available_tools[tool_name]
        required_params = list(tool_spec["parameters"].keys())
        
        # Check if all required parameters are provided
        for param in required_params:
            if param not in parameters:
                return False
        
        return True
    
    async def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get the schema for a specific tool."""
        
        if tool_name in self.available_tools:
            return {
                "name": tool_name,
                **self.available_tools[tool_name]
            }
        
        return {}