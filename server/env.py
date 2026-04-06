from fastapi import FastAPI, HTTPException
from typing import Optional

from server.models import ConfigDebugAction, ConfigDebugObservation, ConfigDebugState
from server.tasks.task_registry import get_task, get_all_task_ids, TASK_ORDER

app = FastAPI(title="ConfigDebugEnv", version="1.0.0")

# --- Environment State ---
MAX_STEPS_PER_TASK = 5


class EnvironmentState:
    """Mutable environment state that persists across requests."""

    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.task_ids = list(TASK_ORDER)
        self.current_task_index = 0
        self.current_step = 0
        self.total_reward = 0.0
        self.is_done = False
        self.tasks_completed = []
        self.bugs_found_so_far = 0
        self.previous_reward = 0.0
        self.current_error_message: Optional[str] = None
        self.current_broken_config: Optional[str] = None


env_state = EnvironmentState()


def _get_current_task_id() -> str:
    if env_state.current_task_index < len(env_state.task_ids):
        return env_state.task_ids[env_state.current_task_index]
    return env_state.task_ids[-1]


def _build_observation() -> ConfigDebugObservation:
    task_id = _get_current_task_id()
    task = get_task(task_id)

    broken_config = (
        env_state.current_broken_config
        if env_state.current_broken_config is not None
        else task.broken_config
    )
    error_message = (
        env_state.current_error_message
        if env_state.current_error_message is not None
        else task.error_message
    )

    return ConfigDebugObservation(
        broken_config=broken_config,
        file_type=task.file_type,
        error_message=error_message,
        task_id=task.task_id,
        task_description=task.description,
        difficulty=task.difficulty,
        num_bugs=task.num_bugs,
        bugs_found_so_far=env_state.bugs_found_so_far,
        previous_reward=env_state.previous_reward,
    )


def _build_state() -> ConfigDebugState:
    task_id = _get_current_task_id()
    tasks_remaining = env_state.task_ids[env_state.current_task_index:]
    if env_state.is_done:
        tasks_remaining = []

    return ConfigDebugState(
        current_task_id=task_id,
        current_step=env_state.current_step,
        max_steps=MAX_STEPS_PER_TASK,
        total_reward=round(env_state.total_reward, 4),
        is_done=env_state.is_done,
        tasks_completed=list(env_state.tasks_completed),
        tasks_remaining=tasks_remaining,
    )


# --- API Endpoints ---


@app.get("/")
def root():
    return {"name": "ConfigDebugEnv", "version": "1.0.0", "status": "running"}


@app.post("/reset")
def reset():
    """Reset the environment to initial state, return first observation."""
    env_state.reset_state()

    observation = _build_observation()
    state = _build_state()

    return {
        "observation": observation.model_dump(),
        "state": state.model_dump(),
    }


@app.post("/step")
def step(action: ConfigDebugAction):
    """
    Take a step in the environment.
    The agent submits a fixed config, the grader evaluates it.
    """
    if env_state.is_done:
        raise HTTPException(
            status_code=400,
            detail="Environment is done. Call /reset to start a new episode.",
        )

    task_id = _get_current_task_id()
    task = get_task(task_id)

    # Run the grader
    reward, error_message, bugs_fixed = task.grader(action.fixed_config)

    env_state.current_step += 1
    env_state.bugs_found_so_far = len(bugs_fixed)
    env_state.previous_reward = round(reward, 4)

    # Update error message for feedback
    env_state.current_error_message = error_message

    # Check if task is complete (perfect score or max steps reached)
    task_done = reward >= 1.0 or env_state.current_step >= MAX_STEPS_PER_TASK

    task_reward = reward  # Reward for this step

    if task_done:
        # Record the best reward for this task
        env_state.total_reward += reward
        env_state.tasks_completed.append(task_id)
        env_state.current_task_index += 1

        # Reset per-task state
        env_state.current_step = 0
        env_state.bugs_found_so_far = 0
        env_state.current_error_message = None
        env_state.current_broken_config = None

        # Check if all tasks are done
        if env_state.current_task_index >= len(env_state.task_ids):
            env_state.is_done = True
    else:
        # If the agent submitted something, use it as the new "broken" config
        # so the agent can iterate
        env_state.current_broken_config = action.fixed_config

    observation = _build_observation()
    state = _build_state()

    return {
        "observation": observation.model_dump(),
        "reward": round(task_reward, 4),
        "done": env_state.is_done,
        "state": state.model_dump(),
        "info": {
            "task_id": task_id,
            "bugs_fixed": bugs_fixed,
            "error_message": error_message,
            "task_done": task_done,
        },
    }


@app.get("/state")
def state():
    """Return current environment state."""
    return _build_state().model_dump()


@app.get("/observation")
def observation():
    """Return current observation."""
    if env_state.is_done:
        raise HTTPException(
            status_code=400,
            detail="Environment is done. Call /reset to start a new episode.",
        )
    return _build_observation().model_dump()
