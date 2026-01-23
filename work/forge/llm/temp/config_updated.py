"""
Configuration for Episodic IPD LLM Agents
Defines hyperparameters for the simulation
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class EpisodeConfig:
    """Configuration for episodic IPD simulation"""
    
    # Episode structure
    num_episodes: int = 5
    rounds_per_episode: int = 20
    
    # Context management
    reset_conversation_between_episodes: bool = True
    history_window_size: int = 10
    
    # Agent parameters
    temperature: float = 0.7
    model_0: str = "llama3:8b-instruct-q5_K_M"
    host_0: str = "iron"
    model_1: str = "llama3:8b-instruct-q5_K_M"
    host_1: str = "iron"
    
    # LLM generation parameters (high-risk - can cause truncation/failures)
    decision_token_limit: int = 256      # Max tokens for decision responses
    reflection_token_limit: int = 1024   # Max tokens for reflection responses
    http_timeout: int = 60               # Seconds to wait for LLM response
    force_decision_retries: int = 2      # Retries for ambiguous decisions
    
    # Reflection parameters
    reflection_prompt_type: Literal["minimal", "standard", "detailed"] = "standard"
    include_statistics: bool = True
    show_other_agent_score: bool = True
    
    # Payoff matrix
    temptation: int = 5  # T
    reward: int = 3      # R
    punishment: int = 1  # P
    sucker: int = 0      # S
    
    # Output
    verbose: bool = True
    
    @property
    def total_rounds(self) -> int:
        """Total number of rounds in the simulation"""
        return self.num_episodes * self.rounds_per_episode
    
    @property
    def payoff_matrix(self) -> dict:
        """Return the payoff matrix as a dictionary"""
        return {
            ('COOPERATE', 'COOPERATE'): (self.reward, self.reward),
            ('COOPERATE', 'DEFECT'): (self.sucker, self.temptation),
            ('DEFECT', 'COOPERATE'): (self.temptation, self.sucker),
            ('DEFECT', 'DEFECT'): (self.punishment, self.punishment),
        }
    
    def validate(self) -> bool:
        """Validate that configuration satisfies IPD constraints"""
        # IPD constraints: T > R > P > S and 2R > T + S
        if not (self.temptation > self.reward > self.punishment > self.sucker):
            raise ValueError(f"Payoff matrix must satisfy T > R > P > S")
        if not (2 * self.reward > self.temptation + self.sucker):
            raise ValueError(f"Payoff matrix must satisfy 2R > T + S")
        return True


# Predefined configurations for experiments

BASELINE_CONFIG = EpisodeConfig(
    num_episodes=5,
    rounds_per_episode=20,
    reset_conversation_between_episodes=True,
    temperature=0.7,
    reflection_prompt_type="standard",
    include_statistics=True,
)

SHORT_LEARNING_CONFIG = EpisodeConfig(
    num_episodes=10,
    rounds_per_episode=10,
    reset_conversation_between_episodes=True,
    temperature=0.7,
    reflection_prompt_type="minimal",
    include_statistics=True,
)

LONG_CONTEXT_CONFIG = EpisodeConfig(
    num_episodes=3,
    rounds_per_episode=50,
    reset_conversation_between_episodes=False,
    temperature=0.7,
    reflection_prompt_type="detailed",
    include_statistics=True,
)

HIGH_EXPLORATION_CONFIG = EpisodeConfig(
    num_episodes=5,
    rounds_per_episode=20,
    reset_conversation_between_episodes=True,
    temperature=1.0,
    reflection_prompt_type="standard",
    include_statistics=True,
)
