f=open("pyproject.toml","w",newline="\n")
f.write("[project]\nname = "config-debug-env"\nversion = "1.0.0"\ndescription = "An RL environment for debugging broken configuration files"\nrequires-python = ">=3.10"\ndependencies = [\n    "fastapi",\n    "uvicorn",\n    "pydantic",\n    "pyyaml",\n    "httpx",\n    "openai",\n    "gradio",\n]\n\n[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.backends._legacy:_Backend"\n")
f.close()
print("Done")
