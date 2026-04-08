"""FastAPI server for ConfigDebugEnv using OpenEnv's create_app."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server import create_app
from server.models import ConfigDebugAction, ConfigDebugObservation
from server.environment import ConfigDebugEnvironment

app = create_app(
    env=ConfigDebugEnvironment,
    action_cls=ConfigDebugAction,
    observation_cls=ConfigDebugObservation,
    env_name="config_debug_env",
)
