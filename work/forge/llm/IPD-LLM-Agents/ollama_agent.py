"""
Ollama Agent wrapper for IPD experiments
"""

import requests
from typing import Optional
import time


class OllamaAgent:
    """An agent that uses Ollama LLM for decision-making in IPD"""
    
    def __init__(
        self,
        agent_id: str,
        model: str,
        host: str = "iron",
        port: int = 11434,
        temperature: float = 0.7,
        system_prompt: str = ""
    ):
        """
        Initialize an Ollama agent
        
        Args:
            agent_id: Unique identifier for this agent (e.g., "agent_0")
            model: Model name (e.g., "llama3:8b-instruct-q5_K_M")
            host: Hostname of Ollama server
            port: Port number
            temperature: Sampling temperature (0.0 = deterministic, higher = more random)
            system_prompt: System prompt defining the agent's role
        """
        self.agent_id = agent_id
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.temperature = temperature
        self.system_prompt = system_prompt
        
        # Conversation history (for in-context learning)
        self.conversation = []
        if system_prompt:
            self.conversation.append({
                "role": "system",
                "content": system_prompt
            })
    
    def generate(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            max_retries: Number of times to retry on failure
            
        Returns:
            Generated text, or None if all retries fail
        """
        # Add user message to conversation
        self.conversation.append({
            "role": "user",
            "content": prompt
        })
        
        # Prepare API request
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": self.conversation,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": 256  # Limit response length
            }
        }
        
        # Try to get response with retries
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                assistant_message = result['message']['content']
                
                # Add assistant response to conversation history
                self.conversation.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                return assistant_message
                
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  {self.agent_id} API error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    return None
        
        return None
    
    def reset_conversation(self, keep_system_prompt: bool = True):
        """
        Reset the conversation history
        
        Args:
            keep_system_prompt: If True, keep the system prompt
        """
        if keep_system_prompt and self.system_prompt:
            self.conversation = [{
                "role": "system",
                "content": self.system_prompt
            }]
        else:
            self.conversation = []
    
    def get_conversation_length(self) -> int:
        """Return the number of messages in conversation history"""
        return len(self.conversation)
    
    def __repr__(self) -> str:
        return f"OllamaAgent(id={self.agent_id}, model={self.model}, conv_length={len(self.conversation)})"
