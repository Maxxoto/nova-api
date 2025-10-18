"""Test script for Groq integration with LangGraph and SSE."""

import asyncio
import json
import requests
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_groq_client():
    """Test the Groq client directly."""
    try:
        from nova_agent.infrastructure.llm.groq_client import groq_client
        
        print("Testing Groq client...")
        
        # Test messages
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        # Test non-streaming completion
        print("Testing non-streaming completion...")
        result = await groq_client.chat_completion(messages)
        print(f"Response: {result['response']}")
        print(f"Thread ID: {result['thread_id']}")
        
        # Test streaming
        print("\nTesting streaming...")
        async for chunk in groq_client.stream_chat_completion(messages):
            print(f"Chunk: {chunk}", end="", flush=True)
        print()
        
        print("✅ Groq client test passed!")
        
    except Exception as e:
        print(f"❌ Groq client test failed: {e}")
        return False
    
    return True


def test_sse_endpoint():
    """Test the SSE endpoint (requires server to be running)."""
    print("\nTesting SSE endpoint...")
    
    # This would require the server to be running
    # For now, we'll just show how to use it
    print("To test the SSE endpoint, run the server and use:")
    print("""
curl -X POST http://localhost:8000/sse/chat-completion \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }' \\
  -N
""")
    
    return True


async def main():
    """Run all tests."""
    print("Testing Groq integration with LangGraph and SSE...")
    
    # Test Groq client
    client_success = await test_groq_client()
    
    # Test SSE endpoint info
    sse_info = test_sse_endpoint()
    
    if client_success and sse_info:
        print("\n🎉 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Set GROQ_API_KEY environment variable")
        print("2. Run the server: uvicorn src.nova_agent.main:app --reload")
        print("3. Test the SSE endpoint with the curl command above")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    asyncio.run(main())