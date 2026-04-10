"""FastAPI application for ConfigDebugEnv.

Uses OpenEnv's create_fastapi_app() for standard framework compatibility
(WebSocket sessions, standard endpoints, grader discovery).
"""
import json
import gradio as gr

from openenv.core.env_server import create_fastapi_app
from server.models import ConfigDebugAction, ConfigDebugObservation, ConfigDebugState
from server.config_debug_environment import ConfigDebugEnvironment
from server.tasks.task_registry import get_task, TASK_ORDER

# ---- Create the standard OpenEnv FastAPI app ----
# create_fastapi_app expects a callable (factory) that returns an Environment
app = create_fastapi_app(
    ConfigDebugEnvironment,       # factory / class — called per session
    ConfigDebugAction,            # action model (inherits Action)
    ConfigDebugObservation,       # observation model (inherits Observation)
)

# Override the default /metadata route with our version that includes tasks
# We need to find and replace the route in the router
for i, route in enumerate(app.router.routes):
    if hasattr(route, 'path') and route.path == '/metadata':
        app.router.routes.pop(i)
        break


# ---- Custom endpoints ----

@app.get("/info")
def info():
    return {"name": "ConfigDebugEnv", "version": "1.0.0", "status": "running"}


@app.get("/metadata")
def metadata():
    return {
        "env_name": "config_debug_env",
        "name": "config_debug_env",
        "version": "1.0.0",
        "description": "Config file debugging environment",
        "tasks": [
            {
                "id": "task1_json", "name": "JSON Config Debug",
                "difficulty": "easy", "num_bugs": 2, "has_grader": True,
                "grader": "server.graders.json_grader:grade_task1",
            },
            {
                "id": "task2_yaml", "name": "YAML Config Debug",
                "difficulty": "easy", "num_bugs": 2, "has_grader": True,
                "grader": "server.graders.yaml_grader:grade_task2",
            },
            {
                "id": "task3_dockerfile", "name": "Dockerfile Debug",
                "difficulty": "medium", "num_bugs": 3, "has_grader": True,
                "grader": "server.graders.dockerfile_grader:grade_task3",
            },
            {
                "id": "task4_compose", "name": "Docker Compose Debug",
                "difficulty": "medium", "num_bugs": 4, "has_grader": True,
                "grader": "server.graders.compose_grader:grade_task4",
            },
            {
                "id": "task5_k8s", "name": "Kubernetes Config Debug",
                "difficulty": "hard", "num_bugs": 5, "has_grader": True,
                "grader": "server.graders.k8s_grader:grade_task5",
            },
            {
                "id": "task6_github_actions", "name": "GitHub Actions Debug",
                "difficulty": "hard", "num_bugs": 5, "has_grader": True,
                "grader": "server.graders.github_actions_grader:grade_task6",
            },
            {
                "id": "task7_nginx", "name": "Nginx Config Debug",
                "difficulty": "very_hard", "num_bugs": 6, "has_grader": True,
                "grader": "server.graders.nginx_grader:grade_task7",
            },
        ],
        "action_model": "ConfigDebugAction",
        "observation_model": "ConfigDebugObservation",
        "state_model": "ConfigDebugState",
    }


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {
                "id": tid,
                "name": get_task(tid).description,
                "difficulty": get_task(tid).difficulty,
                "file_type": get_task(tid).file_type,
                "num_bugs": get_task(tid).num_bugs,
                "has_grader": True,
            }
            for tid in TASK_ORDER
        ],
        "total_tasks": len(TASK_ORDER),
        "tasks_with_graders": len(TASK_ORDER),
    }


# ---- Gradio Web UI ----

_ui_env = ConfigDebugEnvironment()


def ui_reset():
    _ui_env.reset()
    obs = _ui_env._build_observation()
    return (
        f"Task: {obs.task_id} | Difficulty: {obs.difficulty} | Bugs: {obs.num_bugs}",
        obs.task_description,
        obs.broken_config,
        obs.error_message,
        json.dumps({"episode_id": _ui_env._episode_id, "step_count": _ui_env._global_step, "total_reward": _ui_env.total_reward, "tasks_completed": _ui_env.tasks_completed}, indent=2),
        "Environment reset. Submit a fixed config to begin.",
    )


def ui_step(fixed_config):
    if _ui_env._done:
        return (
            "All tasks completed!",
            "",
            "",
            "Episode done. Click Reset to start again.",
            json.dumps({"total_reward": _ui_env.total_reward, "tasks_completed": _ui_env.tasks_completed}, indent=2),
            f"Final score: {_ui_env.total_reward:.1f} / {len(TASK_ORDER)}.0",
        )

    action = ConfigDebugAction(fixed_config=fixed_config)
    obs = _ui_env.step(action)

    history = f"Reward: {obs.reward:.2f} | Bugs found: {obs.bugs_found_so_far}/{obs.num_bugs}\nFeedback: {obs.error_message}"
    return (
        f"Task: {obs.task_id} | Difficulty: {obs.difficulty} | Bugs: {obs.num_bugs}",
        obs.task_description,
        obs.broken_config,
        obs.error_message,
        json.dumps({"episode_id": _ui_env._episode_id, "step_count": _ui_env._global_step, "total_reward": _ui_env.total_reward, "tasks_completed": _ui_env.tasks_completed}, indent=2),
        history,
    )


with gr.Blocks(title="ConfigDebugEnv") as demo:
    gr.Markdown("# ConfigDebugEnv")
    gr.Markdown("An RL environment for debugging broken config files across 7 real-world formats.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Agent Interface")
            task_info = gr.Textbox(label="Current Task", interactive=False)
            task_desc = gr.Textbox(label="Task Description", interactive=False, lines=2)
            broken_config = gr.Textbox(label="Broken Config", interactive=False, lines=10)
            error_msg = gr.Textbox(label="Error Message", interactive=False, lines=2)

            gr.Markdown("### Take Action")
            fixed_config_input = gr.Textbox(label="Your Fixed Config", placeholder="Paste your fixed configuration here...", lines=10)
            with gr.Row():
                reset_btn = gr.Button("Reset Environment", variant="secondary")
                step_btn = gr.Button("Step", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("### State Observer")
            state_display = gr.Textbox(label="Current State", interactive=False, lines=12)
            history_display = gr.Textbox(label="Action History / Reward", interactive=False, lines=4)

    reset_btn.click(
        fn=ui_reset,
        outputs=[task_info, task_desc, broken_config, error_msg, state_display, history_display],
    )
    step_btn.click(
        fn=ui_step,
        inputs=[fixed_config_input],
        outputs=[task_info, task_desc, broken_config, error_msg, state_display, history_display],
    )

app = gr.mount_gradio_app(app, demo, path="/")


def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
