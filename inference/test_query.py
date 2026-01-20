#!/usr/bin/env python3
"""
Test script for DeepResearch with single query.
Uses OpenRouter API with Tavily search.
"""
import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add inference directory to path
sys.path.insert(0, str(Path(__file__).parent))

from react_agent import MultiTurnReactAgent

def main():
    # Test query
    test_query = "中国国足的一场比赛，国足首先失球，由一名宿姓球员扳平了。后来还发生了点球。比分最终是平局。这是哪场比赛"
    
    print("=" * 60)
    print("DeepResearch Test")
    print("=" * 60)
    print(f"Query: {test_query}")
    print(f"Model: {os.environ.get('OPENAI_MODEL', 'Not set')}")
    print(f"API Base: {os.environ.get('OPENAI_BASE_URL', 'Not set')}")
    print("=" * 60)
    
    # LLM configuration
    llm_cfg = {
        'model': os.environ.get('OPENAI_MODEL', 'alibaba/tongyi-deepresearch-30b-a3b'),
        'generate_cfg': {
            'max_input_tokens': 320000,
            'max_retries': 10,
            'temperature': float(os.environ.get('TEMPERATURE', 0.6)),
            'top_p': 0.95,
            'presence_penalty': float(os.environ.get('PRESENCE_PENALTY', 1.1)),
        }
    }
    
    # Create agent
    agent = MultiTurnReactAgent(
        llm=llm_cfg,
        function_list=["search", "visit"]
    )
    
    # Prepare data
    data = {
        'item': {
            'question': test_query,
            'answer': ''  # Unknown answer for testing
        },
        'planning_port': None  # Not used when using OpenRouter
    }
    
    # Run agent
    print("\n>>> Starting agent execution...\n")
    result = agent._run(data, llm_cfg['model'])
    
    # Print results
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Question: {result.get('question', 'N/A')}")
    print(f"\nPrediction: {result.get('prediction', 'N/A')}")
    print(f"\nTermination: {result.get('termination', 'N/A')}")
    
    # Print conversation history
    print("\n" + "=" * 60)
    print("CONVERSATION HISTORY")
    print("=" * 60)
    messages = result.get('messages', [])
    for i, msg in enumerate(messages):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        # Truncate long content for display
        if len(content) > 500:
            content = content[:500] + "... [truncated]"
        print(f"\n[{i}] {role.upper()}:")
        print(content)
    
    return result


if __name__ == "__main__":
    main()
