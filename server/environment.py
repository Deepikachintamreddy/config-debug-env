"""ConfigDebug Environment — OpenEnv Environment implementation."""

from uuid import uuid4
from typing import Optional

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from server.models import ConfigDebugAction, ConfigDebugObservation
from server.tasks.task_registry import get_task, TASK_ORDER


MAX_STEPS_PER_TASK = 5


class ConfigDebugEnvironment(Environment):
    """
    An environment where an AI agent debugs broken configuration files.
    7 tasks cycling through JSON, YAML, Dockerfile, docker-compose,
    Kubernetes, GitHub Actions, and nginx configs.
    """

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_ids = list(TASK_ORDER)
        self._current_task_index = 0
        self._current_step = 0
        self._total_reward = 0.0
        self._is_done = False
        self._tasks_completed = []
        self._bugs_found_so_far = 0
        self._previous_reward = 0.0
        self._current_error_message: Optional[str] = None
        self._current_broken_config: Optional[str] = None

    def _get_current_task_id(self) -> str:
        if self._current_task_index < len(self._task_ids):
            return self._task_ids[self._current_task_index]
        return self._task_ids[-1]

    def reset(self, **kwargs) -> ConfigDebugObservation:
        """Reset the environment to initial state."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_ids = list(TASK_ORDER)
        self._current_task_index = 0
        self._current_step = 0
        self._total_reward = 0.0
        self._is_done = False
        self._tasks_completed = []
        self._bugs_found_so_far = 0
        self._previous_reward = 0.0
        self._current_error_message = None
        self._current_broken_config = None

        task_id = self._get_current_task_id()
        task = get_task(task_id)

        return ConfigDebugObservation(
            broken_config=task.broken_config,
            file_type=task.file_type,
            error_message=task.error_message,
            task_id=task.task_id,
            task_description=task.description,
            difficulty=task.difficulty,
            num_bugs=task.num_bugs,
            bugs_found_so_far=0,
            previous_reward=0.0,
        )

    def step(self, action: ConfigDebugAction) -> ConfigDebugObservation:
        """Execute agent's fix attempt and grade it."""
        if self._is_done:
            task_id = self._get_current_task_id()
            task = get_task(task_id)
            return ConfigDebugObservation(
                broken_config="",
                file_type="",
                error_message="Episode is done. Call reset() to start a new one.",
                task_id=task_id,
                task_description="",
                difficulty="",
                num_bugs=0,
                bugs_found_so_far=0,
                previous_reward=0.0,
                done=True,
                reward=0.0,
            )

        task_id = self._get_current_task_id()
        task = get_task(task_id)

        # Run the grader
        reward, error_message, bugs_fixed = task.grader(action.fixed_config)

        self._current_step += 1
        self._state.step_count += 1
        self._bugs_found_so_far = len(bugs_fixed)
        self._previous_reward = round(reward, 4)
        self._current_error_message = error_message

        # Check if task is complete
        task_done = reward >= 1.0 or self._current_step >= MAX_STEPS_PER_TASK

        if task_done:
            self._total_reward += reward
            self._tasks_completed.append(task_id)
            self._current_task_index += 1
            self._current_step = 0
            self._bugs_found_so_far = 0
            self._current_error_message = None
            self._current_broken_config = None

            if self._current_task_index >= len(self._task_ids):
                self._is_done = True
        else:
            self._current_broken_config = action.fixed_config

        # Build next observation
        if self._is_done:
            return ConfigDebugObservation(
                broken_config="",
                file_type="",
                error_message="All tasks completed!",
                task_id=task_id,
                task_description="",
                difficulty="",
                num_bugs=0,
                bugs_found_so_far=0,
                previous_reward=round(reward, 4),
                done=True,
                reward=round(reward, 4),
            )

        next_task_id = self._get_current_task_id()
        next_task = get_task(next_task_id)

        broken_config = (
            self._current_broken_config
            if self._current_broken_config is not None
            else next_task.broken_config
        )
        err_msg = (
            self._current_error_message
            if self._current_error_message is not None
            else next_task.error_message
        )

        return ConfigDebugObservation(
            broken_config=broken_config,
            file_type=next_task.file_type,
            error_message=err_msg,
            task_id=next_task.task_id,
            task_description=next_task.description,
            difficulty=next_task.difficulty,
            num_bugs=next_task.num_bugs,
            bugs_found_so_far=self._bugs_found_so_far,
            previous_reward=round(reward, 4),
            done=False,
            reward=round(reward, 4),
        )

    @property
    def state(self) -> State:
        return self._state
