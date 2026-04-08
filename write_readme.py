import os
readme = '''---
title: ConfigDebugEnv
colorFrom: red
colorTo: yellow
sdk: docker
app_port: 7860
tags:
  - openenv
  - devops
  - configuration
  - debugging
pinned: false
---

# ConfigDebugEnv

An RL environment where AI agents learn to debug broken configuration files across 7 real-world formats. Built for the Meta PyTorch OpenEnv Hackathon x SST.

## Real-World Problem

Configuration file errors are one of the most common causes of deployment failures and CI/CD pipeline breakdowns. ConfigDebugEnv trains AI agents to identify and fix these bugs automatically across JSON, YAML, Dockerfile, docker-compose, Kubernetes, GitHub Actions, and nginx configs.

## Tasks

- task1_json (Easy, 2 bugs) - App config with missing comma and wrong type
- task2_yaml (Easy, 2 bugs) - Service config with indentation and missing field
- task3_dockerfile (Medium, 3 bugs) - Multi-stage build with syntax and logic errors
- task4_compose (Medium, 4 bugs) - Multi-service setup with networking issues
- task5_k8s (Hard, 5 bugs) - Deployment manifest with label and spec errors
- task6_github_actions (Hard, 5 bugs) - CI/CD workflow with trigger and syntax issues
- task7_nginx (Very Hard, 6 bugs) - Reverse proxy config with directive errors

## Action Space

The agent submits: fixed_config (str) - the corrected configuration file content.

## Observation Space

The agent receives: broken_config, file_type, error_message, task_id, task_description, difficulty, num_bugs, bugs_found_so_far, previous_reward.

## Reward Function

Rewards use partial credit: reward = bugs_fixed / total_bugs. Perfect fix = 1.0 and advances to next task. Max 5 attempts per task.

## API Endpoints

- POST /reset - Reset environment
- POST /step - Submit a fixed config
- GET /state - Get current state
- GET /observation - Get current observation
- GET /docs - Swagger API docs

## Setup

Run locally:

    pip install fastapi uvicorn pydantic pyyaml httpx openai gradio
    uvicorn server.env:app --host 0.0.0.0 --port 7860

Run with Docker:

    docker build -t config-debug-env .
    docker run -p 7860:7860 config-debug-env

## Baseline Results

Qwen/Qwen2.5-72B-Instruct: 7/7 tasks, score = 1.000
'''
f = open('README.md', 'w', newline='\n')
f.write(readme)
f.close()
print('Done, size:', len(readme))
