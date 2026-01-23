#!/usr/bin/env python3
"""
Test Ollama connectivity and basic agent functionality
"""

from ollama_agent import OllamaAgent
from prompts import SYSTEM_PROMPT


def test_connection(host: str = "iron", model: str = "llama3:8b-instruct-q5_K_M"):
    """Test basic connection to Ollama service"""
    print(f"Testing connection to {host} with model {model}...")
    
    agent = OllamaAgent(
        agent_id="test_agent",
        model=model,
        host=host,
        temperature=0.7,
        system_prompt=SYSTEM_PROMPT
    )
    
    # Simple test prompt
    test_prompt = """This is a simple test. You are in round 1 of an IPD game.
    
What is your decision? Explain briefly and then state COOPERATE or DEFECT."""
    
    print("\nSending test prompt...")
    response = agent.generate(test_prompt)
    
    if response:
        print(f"\n✅ Success! Agent responded:")
        print(f"{response}")
        print(f"\nConversation length: {agent.get_conversation_length()} messages")
        return True
    else:
        print("\n❌ Failed to get response from agent")
        return False


def test_decision_extraction():
    """Test decision extraction logic"""
    from prompts import extract_decision
    
    print("\nTesting decision extraction...")
    
    test_cases = [
        ("I will COOPERATE because...", "COOPERATE"),
        ("After thinking about it, I choose to DEFECT", "DEFECT"),
        ("My reasoning is X. COOPERATE", "COOPERATE"),
        ("Let me explain...\n\nDEFECT", "DEFECT"),
        ("Cooperate sounds good", None),  # Should fail (not all caps)
        ("I'll cooperate or maybe defect", None),  # Should fail (ambiguous)
    ]
    
    passed = 0
    for response, expected in test_cases:
        result = extract_decision(response)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{response[:50]}...' -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nPassed {passed}/{len(test_cases)} tests")
    return passed == len(test_cases)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Ollama setup for IPD")
    parser.add_argument(
        "--host",
        type=str,
        default="iron",
        help="Ollama host to test (default: iron)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="llama3:8b-instruct-q5_K_M",
        help="Model to test"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("OLLAMA IPD TEST SUITE")
    print("="*60)
    
    # Test extraction logic
    extraction_ok = test_decision_extraction()
    
    print("\n" + "="*60)
    
    # Test connection
    connection_ok = test_connection(args.host, args.model)
    
    print("\n" + "="*60)
    if extraction_ok and connection_ok:
        print("✅ All tests passed! System is ready.")
        print("\nYou can now run:")
        print("  python ipd_llm_game.py --rounds 100")
    else:
        print("❌ Some tests failed. Check configuration.")
    print("="*60)


if __name__ == "__main__":
    main()
