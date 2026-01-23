"""
Ollama Agent wrapper for Episodic IPD experiments
Enhanced with retry logic for ambiguous responses
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
    
    def generate(
        self, 
        prompt: str, 
        max_retries: int = 3,
        num_predict: int = 256,
        is_reflection: bool = False
    ) -> Optional[str]:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            max_retries: Number of times to retry on failure
            num_predict: Maximum tokens to generate (default: 256 for decisions, higher for reflections)
            is_reflection: If True, use higher token limit
            
        Returns:
            Generated text, or None if all retries fail
        """
        # Use higher token limit for reflections
        if is_reflection:
            num_predict = 1024
        
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
                "num_predict": num_predict
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
    
    def generate_with_forced_decision(
        self, 
        prompt: str,
        extract_decision_fn,
        max_retries: int = 2
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Generate a response and retry with simplified prompt if ambiguous
        
        Args:
            prompt: Initial decision prompt
            extract_decision_fn: Function to extract decision from response
            max_retries: Number of times to retry with simplified prompt
            
        Returns:
            (decision, full_response) tuple
        """
        # First attempt with full prompt
        response = self.generate(prompt, num_predict=256)
        
        if response is None:
            return None, None
        
        decision = extract_decision_fn(response)
        
        if decision is not None:
            return decision, response
        
        # Response was ambiguous - retry with forced decision prompt
        for retry in range(max_retries):
            print(f"  ⚠️  {self.agent_id} gave ambiguous response, forcing decision (attempt {retry + 1}/{max_retries})")
            
            # Create a forcing prompt
            force_prompt = """Your previous response did not clearly specify COOPERATE or DEFECT.

You MUST choose exactly one action. This is a fundamental requirement of the game.

Respond with ONLY your reasoning (2-3 sentences) followed by exactly one word on its own line:
COOPERATE
or
DEFECT

What is your decision?"""
            
            response = self.generate(force_prompt, num_predict=256)
            
            if response is None:
                continue
                
            decision = extract_decision_fn(response)
            
            if decision is not None:
                return decision, f"[FORCED DECISION AFTER {retry + 1} RETRIES]\n{response}"
        
        # All retries failed
        return None, response
    
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
    
    def add_reflection_to_context(self, reflection_text: str):
        """
        Add a reflection as a user message to preserve it in context
        
        Args:
            reflection_text: The reflection to add to context
        """
        self.conversation.append({
            "role": "user",
            "content": reflection_text
        })
    
    def get_conversation_length(self) -> int:
        """Return the number of messages in conversation history"""
        return len(self.conversation)
    
    def __repr__(self) -> str:
        return f"OllamaAgent(id={self.agent_id}, model={self.model}, conv_length={len(self.conversation)})"
