TASK_ID = "task5_k8s"
DIFFICULTY = "hard"
FILE_TYPE = "kubernetes"
NUM_BUGS = 5

DESCRIPTION = (
    "A Kubernetes Deployment manifest for a web application. It should deploy 3 replicas "
    "of an nginx-based app container on port 8080, with matching label selectors, a "
    "readinessProbe on the correct port, and reasonable resource limits (at least 128Mi memory)."
)

# Bug 1 (Syntax): Tab character instead of spaces (YAML doesn't allow tabs)
# Bug 2 (Semantic): apiVersion is "apps/v1beta1" (deprecated, should be "apps/v1")
# Bug 3 (Semantic): spec.selector.matchLabels doesn't match template.metadata.labels
# Bug 4 (Runtime): Container port is 8080 but readinessProbe targets port 3000
# Bug 5 (Runtime): Resource limit memory: "50Mi" is too low, should be at least "128Mi"
BROKEN_CONFIG = """apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
\tlabels:
        app: frontend
    spec:
      containers:
      - name: web
        image: nginx:1.24
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /healthz
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "32Mi"
            cpu: "100m"
          limits:
            memory: "50Mi"
            cpu: "500m"""

ERROR_MESSAGE = (
    "Kubernetes manifest error: YAML contains tab characters which are not allowed. "
    "Additionally, the apiVersion may be deprecated, label selectors may not match, "
    "probe ports may be inconsistent with container ports, and resource limits may be "
    "unreasonably low."
)

GROUND_TRUTH = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx:1.24
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "500m"
"""
