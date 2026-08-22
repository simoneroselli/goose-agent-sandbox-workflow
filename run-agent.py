#!/usr/bin/env python3
import os
import sys
import subprocess


IMAGE_NAME = "goose-sandbox:latest"


def ensure_docker_image():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    image_check = subprocess.run(
        ["docker", "image", "inspect", IMAGE_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if image_check.returncode == 0:
        return

    print(f"📦 Docker image {IMAGE_NAME} not found. Building it...")
    subprocess.run(
        ["docker", "buildx", "build", "-f", "Dockerfile", "-t", IMAGE_NAME, "."],
        cwd=repo_dir,
        check=True,
    )


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {os.path.basename(sys.argv[0])} <working-directory-to-mount>")
        sys.exit(1)

    try:
        import yaml
    except ImportError:
        print("❌ PyYAML is required. Run: pip install -r requirements.txt")
        sys.exit(1)

    project_dir = os.path.abspath(sys.argv[1])
    config_path = os.path.join(project_dir, "agent-config.yaml")

    if not os.path.exists(config_path):
        print(f"❌ Error: No agent-config.yaml found at {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    provider = config.get("provider", "openai")
    model = config.get("model", "qwen3.8-27b")
    host = config.get("host", "http://localhost:1234/v1")
    mode = config.get("mode", "approve")
    
    # Read developer extension preference (default to False for safety)
    dev_enabled = config.get("extensions", {}).get("developer", False)

    print(f"🚀 Launching Goose for project: {config.get('project_name', 'Unknown')}")
    print(f"🔒 Developer Extension Enabled: {dev_enabled}")

    # Generate a temporary config file inside a local temp dir to mount into the container
    container_config_dir = os.path.expanduser("~/.config/goose")
    os.makedirs(container_config_dir, exist_ok=True)
    
    goose_app_config = {
        "extensions": {
            "developer": {
                "type": "builtin",
                "name": "developer",
                "enabled": dev_enabled,
                "bundled": True
            }
        }
    }
    
    app_config_path = os.path.join(container_config_dir, "config.yaml")
    with open(app_config_path, "w") as cf:
        yaml.dump(goose_app_config, cf)

    ensure_docker_image()

    # Build the Docker command with unprivileged security flags
    docker_cmd = [
        "docker", "run", "-it", "--rm",
        "--user", "1001:1001",
        "--security-opt", "no-new-privileges=true",
        "-v", f"{project_dir}:/workspace",
        "-v", f"{container_config_dir}:/home/agentuser/.config/goose",
        "-e", f"GOOSE_PROVIDER={provider}",
        "-e", f"GOOSE_MODEL={model}",
        "-e", f"GOOSE_PROVIDER__HOST={host}",
        "-e", f"GOOSE_PROVIDER__API_KEY=not-needed",
        "-e", f"GOOSE_MODE={mode}",
        "-e", f"GOOSE_WORKING_DIR=/workspace",
        IMAGE_NAME,
        "goose", "session"
    ]

    subprocess.run(docker_cmd)

if __name__ == "__main__":
    main()