import re
from typing import Tuple, List


def _check_braces_balanced(config: str) -> bool:
    """Check if all braces are balanced in the config."""
    count = 0
    for ch in config:
        if ch == "{":
            count += 1
        elif ch == "}":
            count -= 1
        if count < 0:
            return False
    return count == 0


def _check_semicolons(config: str) -> List[str]:
    """Check that directives end with semicolons. Returns list of issues."""
    issues = []
    directives_needing_semicolons = [
        "server_name", "listen", "ssl_certificate", "ssl_certificate_key",
        "proxy_pass", "proxy_set_header", "worker_processes", "worker_connections",
        "alias", "expires", "access_log", "return", "add_header",
        "client_max_body_size", "keepalive_timeout",
    ]

    lines = config.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Check if line starts with a directive that needs semicolon
        for directive in directives_needing_semicolons:
            if stripped.startswith(directive):
                # These directives should end with ;
                if not stripped.endswith(";") and not stripped.endswith("{"):
                    issues.append(
                        f"Line {i + 1}: directive '{directive}' is missing a "
                        f"trailing semicolon"
                    )
                break
    return issues


def grade_task7(submitted_config: str) -> Tuple[float, str, List[str]]:
    """
    Grade Task 7: Broken nginx.conf (6 bugs)
    Bug 1 (Syntax): Missing semicolon at end of server_name directive
    Bug 2 (Syntax): Unclosed brace in location block
    Bug 3 (Semantic): proxy_pass URL has wrong port (8080, backend runs on 3000)
    Bug 4 (Semantic): ssl_certificate path points to non-standard location
    Bug 5 (Runtime): worker_connections set to 10 (too low, should be 1024+)
    Bug 6 (Integration): upstream "app_server" but proxy_pass references "http://backend"

    Returns: (reward, error_message, bugs_fixed_list)
    """
    bugs_fixed = []
    total_bugs = 6
    error_messages = []

    lines = submitted_config.split("\n")

    # Bug 1: Check server_name has semicolon
    server_name_ok = True
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("server_name"):
            if stripped.endswith(";"):
                bugs_fixed.append("server_name_semicolon")
            else:
                server_name_ok = False
                error_messages.append(
                    "server_name directive is missing a trailing semicolon."
                )
            break

    # Bug 2: Check braces are balanced
    if _check_braces_balanced(submitted_config):
        bugs_fixed.append("braces_balanced")
    else:
        error_messages.append(
            "Configuration has unbalanced braces. Check that all '{' have "
            "matching '}', especially in location blocks."
        )

    # Bug 5: Check worker_connections
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("worker_connections"):
            match = re.search(r"worker_connections\s+(\d+)", stripped)
            if match:
                wc = int(match.group(1))
                if wc >= 1024:
                    bugs_fixed.append("worker_connections_reasonable")
                else:
                    error_messages.append(
                        f"worker_connections is {wc}, which is unrealistically low. "
                        f"Should be at least 1024 for a production server."
                    )
            break

    # Bug 4: Check SSL certificate paths
    ssl_cert_ok = False
    ssl_key_ok = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("ssl_certificate_key"):
            # Check key path is standard
            match = re.search(r"ssl_certificate_key\s+(.+);", stripped)
            if match:
                path = match.group(1).strip()
                if path.startswith("/etc/ssl/") or path.startswith("/etc/nginx/ssl/"):
                    ssl_key_ok = True
                else:
                    error_messages.append(
                        f"ssl_certificate_key path '{path}' is non-standard. "
                        f"Use /etc/ssl/private/ or /etc/nginx/ssl/."
                    )
        elif stripped.startswith("ssl_certificate"):
            match = re.search(r"ssl_certificate\s+(.+);", stripped)
            if match:
                path = match.group(1).strip()
                if path.startswith("/etc/ssl/") or path.startswith("/etc/nginx/ssl/"):
                    ssl_cert_ok = True
                else:
                    error_messages.append(
                        f"ssl_certificate path '{path}' is non-standard. "
                        f"Use /etc/ssl/certs/ or /etc/nginx/ssl/."
                    )

    if ssl_cert_ok and ssl_key_ok:
        bugs_fixed.append("ssl_paths_standard")
    elif not ssl_cert_ok and not ssl_key_ok:
        error_messages.append(
            "Both ssl_certificate and ssl_certificate_key paths are non-standard."
        )

    # Bug 6: Check upstream name matches proxy_pass
    upstream_names = set()
    for line in lines:
        match = re.search(r"upstream\s+(\S+)\s*\{", line)
        if match:
            upstream_names.add(match.group(1))

    proxy_pass_targets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("proxy_pass"):
            match = re.search(r"proxy_pass\s+https?://([^:/;\s]+)", stripped)
            if match:
                proxy_pass_targets.append(match.group(1))

    upstream_match = True
    for target in proxy_pass_targets:
        if upstream_names and target not in upstream_names:
            # Target is not an upstream name - could be direct IP/hostname
            # But if we have upstreams defined, proxy_pass should reference them
            upstream_match = False
            error_messages.append(
                f"proxy_pass references '{target}' but defined upstream(s) are "
                f"{sorted(upstream_names)}. proxy_pass should reference the upstream name."
            )

    if upstream_match and upstream_names:
        bugs_fixed.append("upstream_name_matches")
    elif not upstream_names:
        error_messages.append("No upstream block defined")

    # Bug 3: Check proxy_pass port (should not have port if using upstream,
    # or should be 3000 if direct)
    proxy_port_ok = True
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("proxy_pass"):
            # If using upstream (no port), it's correct
            # If using direct host:port, port should be 3000
            match = re.search(r"proxy_pass\s+https?://[^:;\s]+:(\d+)", stripped)
            if match:
                port = int(match.group(1))
                if port == 8080:
                    proxy_port_ok = False
                    error_messages.append(
                        f"proxy_pass port is {port} but the backend application "
                        f"runs on port 3000."
                    )
            # If no port and using upstream name, that's correct
            break

    if proxy_port_ok:
        bugs_fixed.append("proxy_pass_port_correct")

    # Calculate reward
    reward = len(bugs_fixed) / total_bugs

    # Bonus for balanced braces
    if "braces_balanced" in bugs_fixed and "server_name_semicolon" in bugs_fixed:
        reward = min(1.0, reward + 0.1)

    if len(bugs_fixed) == total_bugs:
        reward = 1.0

    error_msg = "; ".join(error_messages) if error_messages else "All checks passed!"
    return reward, error_msg, bugs_fixed
