import json
import yaml


def grade_task1(fixed_config: str) -> float:
    try:
        data = json.loads(fixed_config)
        score = 0.01
        if isinstance(data.get("port"), int):
            score += 0.49
        if data.get("app_name"):
            score += 0.49
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task2(fixed_config: str) -> float:
    try:
        data = yaml.safe_load(fixed_config)
        if not isinstance(data, dict):
            return 0.01
        score = 0.01
        if "service" in data or "name" in data:
            score += 0.49
        if "port" in data or "database" in data:
            score += 0.49
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task3(fixed_config: str) -> float:
    try:
        lines = fixed_config.strip().splitlines()
        score = 0.01
        if any("FROM" in l for l in lines):
            score += 0.32
        if any("COPY" in l for l in lines):
            score += 0.32
        if any("RUN" in l for l in lines):
            score += 0.33
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task4(fixed_config: str) -> float:
    try:
        data = yaml.safe_load(fixed_config)
        if not isinstance(data, dict):
            return 0.01
        score = 0.01
        if "services" in data:
            score += 0.32
            services = data["services"]
            if len(services) >= 2:
                score += 0.32
            if any("ports" in str(s) for s in services.values()):
                score += 0.33
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task5(fixed_config: str) -> float:
    try:
        data = yaml.safe_load(fixed_config)
        if not isinstance(data, dict):
            return 0.01
        score = 0.01
        if data.get("kind") == "Deployment":
            score += 0.24
        if "spec" in data:
            score += 0.24
            if "replicas" in data["spec"]:
                score += 0.24
            if "template" in data["spec"]:
                score += 0.25
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task6(fixed_config: str) -> float:
    try:
        data = yaml.safe_load(fixed_config)
        if not isinstance(data, dict):
            return 0.01
        score = 0.01
        if "jobs" in data:
            score += 0.49
            if len(data["jobs"]) >= 1:
                score += 0.49
        return min(0.99, score)
    except Exception:
        return 0.01


def grade_task7(fixed_config: str) -> float:
    try:
        score = 0.01
        if "upstream" in fixed_config:
            score += 0.24
        if "server" in fixed_config:
            score += 0.24
        if "listen" in fixed_config:
            score += 0.24
        if "proxy_pass" in fixed_config:
            score += 0.25
        return min(0.99, score)
    except Exception:
        return 0.01