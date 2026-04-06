import yaml
import re
from typing import Tuple, List


def _parse_memory_value(val: str) -> int:
    """Parse Kubernetes memory value to bytes."""
    val = str(val).strip()
    multipliers = {
        "Ki": 1024,
        "Mi": 1024 ** 2,
        "Gi": 1024 ** 3,
        "Ti": 1024 ** 4,
        "K": 1000,
        "M": 1000 ** 2,
        "G": 1000 ** 3,
    }
    for suffix, mult in multipliers.items():
        if val.endswith(suffix):
            return int(val[: -len(suffix)]) * mult
    try:
        return int(val)
    except ValueError:
        return 0


def grade_task5(submitted_config: str) -> Tuple[float, str, List[str]]:
    """
    Grade Task 5: Broken Kubernetes Deployment YAML (5 bugs)
    Bug 1 (Syntax): Tab character instead of spaces
    Bug 2 (Semantic): apiVersion is "apps/v1beta1" (should be "apps/v1")
    Bug 3 (Semantic): selector.matchLabels doesn't match template.metadata.labels
    Bug 4 (Runtime): Container port is 8080 but readinessProbe targets port 3000
    Bug 5 (Runtime): Resource limit memory "50Mi" too low (should be >= 128Mi)

    Returns: (reward, error_message, bugs_fixed_list)
    """
    bugs_fixed = []
    total_bugs = 5
    error_messages = []

    # Bug 1: Check for tab characters
    if "\t" in submitted_config:
        error_messages.append(
            "YAML contains tab characters. YAML only allows spaces for indentation."
        )
    else:
        bugs_fixed.append("no_tabs")

    # Try to parse YAML
    try:
        config = yaml.safe_load(submitted_config)
        if not isinstance(config, dict):
            error_messages.append("Kubernetes manifest is not a valid mapping")
            reward = len(bugs_fixed) / total_bugs
            return reward, "; ".join(error_messages), bugs_fixed
    except yaml.YAMLError as e:
        error_messages.append(f"YAML parse error: {str(e)}")
        reward = len(bugs_fixed) / total_bugs
        return reward, "; ".join(error_messages), bugs_fixed

    # Bug 2: Check apiVersion
    api_version = config.get("apiVersion", "")
    valid_api_versions = ["apps/v1"]
    if api_version in valid_api_versions:
        bugs_fixed.append("valid_api_version")
    else:
        error_messages.append(
            f"apiVersion '{api_version}' is deprecated or invalid. Use 'apps/v1'."
        )

    # Bug 3: Check label selectors match
    spec = config.get("spec", {})
    selector_labels = (
        spec.get("selector", {}).get("matchLabels", {})
        if isinstance(spec.get("selector"), dict)
        else {}
    )
    template_labels = (
        spec.get("template", {}).get("metadata", {}).get("labels", {})
        if isinstance(spec.get("template", {}).get("metadata"), dict)
        else {}
    )
    if selector_labels and template_labels and selector_labels == template_labels:
        bugs_fixed.append("labels_match")
    else:
        error_messages.append(
            f"selector.matchLabels {selector_labels} does not match "
            f"template.metadata.labels {template_labels}. They must be identical."
        )

    # Bug 4 & 5: Check container spec
    containers = (
        spec.get("template", {}).get("spec", {}).get("containers", [])
        if isinstance(spec.get("template", {}).get("spec"), dict)
        else []
    )
    if containers and isinstance(containers[0], dict):
        container = containers[0]

        # Bug 4: Check port consistency
        container_ports = container.get("ports", [])
        container_port = None
        if container_ports and isinstance(container_ports[0], dict):
            container_port = container_ports[0].get("containerPort")

        readiness_probe = container.get("readinessProbe", {})
        probe_port = None
        if isinstance(readiness_probe, dict):
            http_get = readiness_probe.get("httpGet", {})
            if isinstance(http_get, dict):
                probe_port = http_get.get("port")

        if container_port is not None and probe_port is not None:
            if container_port == probe_port:
                bugs_fixed.append("ports_consistent")
            else:
                error_messages.append(
                    f"Container port is {container_port} but readinessProbe "
                    f"targets port {probe_port}. They should match."
                )
        elif probe_port is None:
            error_messages.append("readinessProbe is missing or misconfigured")

        # Bug 5: Check resource limits
        resources = container.get("resources", {})
        if isinstance(resources, dict):
            limits = resources.get("limits", {})
            if isinstance(limits, dict):
                mem_limit = limits.get("memory", "0")
                mem_bytes = _parse_memory_value(str(mem_limit))
                min_memory = 128 * 1024 * 1024  # 128Mi
                if mem_bytes >= min_memory:
                    bugs_fixed.append("memory_limit_reasonable")
                else:
                    error_messages.append(
                        f"Memory limit '{mem_limit}' is too low. "
                        f"Should be at least '128Mi' for a web application."
                    )
            else:
                error_messages.append("Resource limits are not properly defined")
        else:
            error_messages.append("Resources section is missing")
    else:
        error_messages.append("No containers defined in the pod spec")

    # Calculate reward
    reward = len(bugs_fixed) / total_bugs

    # Bonus for parseable YAML
    if "no_tabs" in bugs_fixed:
        reward = min(1.0, reward + 0.1)

    if len(bugs_fixed) == total_bugs:
        reward = 1.0

    error_msg = "; ".join(error_messages) if error_messages else "All checks passed!"
    return reward, error_msg, bugs_fixed
