"""
Inference Script — ConfigDebugEnv
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    IMAGE_NAME     The name of the local image to use for the environment if you are using
                   from_docker_image() method

STDOUT FORMAT
- The script emits exactly three line types to stdout:
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

import asyncio
import os
import textwrap
from typing import List, Optional

from openai import OpenAI

IMAGE_NAME = os.getenv("IMAGE_NAME")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("CONFIG_DEBUG_TASK", "config-debug")
BENCHMARK = os.getenv("CONFIG_DEBUG_BENCHMARK", "config_debug_env")
MAX_STEPS = 35  # 7 tasks x 5 steps each
TEMPERATURE = 0.1
MAX_TOKENS = 2000
SUCCESS_SCORE_THRESHOLD = 0.5  # normalized score in [0, 1]
MAX_TOTAL_REWARD = 7.0  # 7 tasks, 1.0 max per task

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an expert DevOps engineer specializing in configuration file debugging.
    You will be given a broken configuration file and must fix ALL bugs in it.
    Return ONLY the fixed configuration file content.
    No explanations, no markdown formatting, no code blocks. Just the raw fixed configuration.
    """
).strip()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def strip_code_blocks(text: str) -> str:
    """Remove markdown code blocks if LLM wraps output in them."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        text = "\n".join(lines)
    return text


def build_user_prompt(obs: dict, step: int, history: List[str]) -> str:
    history_block = "\n".join(history[-4:]) if history else "None"
    return textwrap.dedent(
        f"""
        Fix the following broken {obs.get('file_type', 'unknown')} configuration file.

        Task: {obs.get('task_description', '')}
        Difficulty: {obs.get('difficulty', '')}
        Number of bugs to find: {obs.get('num_bugs', 0)}
        Bugs fixed so far: {obs.get('bugs_found_so_far', 0)}
        Error message: {obs.get('error_message', '')}
        Step: {step}

        Previous attempts:
        {history_block}

        Broken configuration:
        ```
        {obs.get('broken_config', '')}
        ```

        Return ONLY the fixed configuration file content.
        """
    ).strip()


def get_model_message(client: OpenAI, obs: dict, step: int, history: List[str]) -> str:
    user_prompt = build_user_prompt(obs, step, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return strip_code_blocks(text) if text else ""
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return ""


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Connect to the environment via HTTP
    import httpx
    import sys

    class HTTPEnvClient:
        """Simple HTTP client that works with both old and new OpenEnv API formats."""

        def __init__(self, base_url: str):
            self.base_url = base_url.rstrip("/")
            self.http = httpx.AsyncClient(timeout=60.0)

        async def reset(self):
            resp = await self.http.post(f"{self.base_url}/reset")
            resp.raise_for_status()
            return resp.json()

        async def step(self, action_data: dict):
            # Try create_app format first: {"action": {...}}
            resp = await self.http.post(
                f"{self.base_url}/step",
                json={"action": action_data},
            )
            if resp.status_code == 422:
                # Fallback to direct format: {...}
                resp = await self.http.post(
                    f"{self.base_url}/step",
                    json=action_data,
                )
            resp.raise_for_status()
            return resp.json()

        async def close(self):
            await self.http.aclose()

    env_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7860"
    env = HTTPEnvClient(env_url)

    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset()
        obs = result["observation"]

        step_num = 0
        done = result.get("done", False)

        while not done:
            step_num += 1

            fixed_config = get_model_message(client, obs, step_num, history)

            step_result = await env.step({"fixed_config": fixed_config})
            obs = step_result["observation"]
            reward = step_result.get("reward", 0.0) or 0.0
            done = step_result.get("done", False)

            # Get error from observation
            error_msg = obs.get("error_message", "")
            error = error_msg if error_msg and error_msg != "All checks passed!" else None

            rewards.append(reward)
            steps_taken = step_num

            task_id = obs.get("task_id", "unknown")
            action_summary = f"fix({task_id})"
            log_step(step=step_num, action=action_summary, reward=reward, done=done, error=error)

            history.append(f"Step {step_num}: {action_summary} -> reward {reward:+.2f}")

            if done or step_num >= MAX_STEPS:
                break

        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            await env.close()
        except Exception as e:
            print(f"[DEBUG] env.close() error: {e}", flush=True)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
