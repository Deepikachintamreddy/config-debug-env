from pydantic import Field
from typing import List
from openenv.core.env_server.types import Action, Observation


class ConfigDebugAction(Action):
    """Action: the agent submits a fixed configuration file"""
    fixed_config: str = Field(..., description="The corrected configuration file content")


class ConfigDebugObservation(Observation):
    """Observation: what the agent sees"""
    broken_config: str = Field(default="", description="The broken configuration file content")
    file_type: str = Field(default="", description="json, yaml, dockerfile, docker-compose, kubernetes, github-actions, nginx")
    error_message: str = Field(default="", description="Error/hint about what's wrong")
    task_id: str = Field(default="", description="e.g., task1_json, task2_yaml")
    task_description: str = Field(default="", description="Human-readable description of what the config should do")
    difficulty: str = Field(default="", description="easy, medium, hard, very_hard")
    num_bugs: int = Field(default=0, description="Total number of bugs in this task")
    bugs_found_so_far: int = Field(default=0, description="How many bugs the agent has fixed in previous steps")
    previous_reward: float = Field(default=0.0, description="Reward from previous step")
