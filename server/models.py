from pydantic import BaseModel
from typing import List


class ConfigDebugAction(BaseModel):
    """Action: the agent submits a fixed configuration file"""
    fixed_config: str  # The corrected configuration file content


class ConfigDebugObservation(BaseModel):
    """Observation: what the agent sees"""
    broken_config: str          # The broken configuration file content
    file_type: str              # "json", "yaml", "dockerfile", "docker-compose", "kubernetes", "github-actions", "nginx"
    error_message: str          # Error/hint about what's wrong
    task_id: str                # e.g., "task1_json", "task2_yaml"
    task_description: str       # Human-readable description of what the config should do
    difficulty: str             # "easy", "medium", "hard", "very_hard"
    num_bugs: int               # Total number of bugs in this task
    bugs_found_so_far: int      # How many bugs the agent has fixed in previous steps
    previous_reward: float      # Reward from previous step (0.0 on first step)


class ConfigDebugState(BaseModel):
    """Full environment state"""
    current_task_id: str
    current_step: int
    max_steps: int              # Maximum steps allowed per task (e.g., 5)
    total_reward: float
    is_done: bool
    tasks_completed: List[str]
    tasks_remaining: List[str]
