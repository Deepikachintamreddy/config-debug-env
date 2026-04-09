import requests
BASE = "https://DeepikaChintamreddy-config-debug-env.hf.space"
r = requests.post(f"{BASE}/reset")
print("Reset:", r.status_code)
obs = r.json()["observation"]
tasks_tested = 0
for i in range(7):
    tid = obs.get("task_id","")
    r = requests.post(f"{BASE}/step", json={"fixed_config": "dummy"})
    d = r.json()
    reward = d.get("reward", 0)
    print(f"Task {tid}: reward={reward}")
    if reward > 0 and reward < 1:
        tasks_tested += 1
    obs = d["observation"]
    if d.get("done", False):
        break
print(f"Tasks with valid scores: {tasks_tested}")
print("PASS" if tasks_tested >= 3 else "FAIL")
