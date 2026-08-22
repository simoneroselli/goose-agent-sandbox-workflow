#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil


IMAGE_NAME = "goose-sandbox:latest"

# Fetch host IDs once at the module level
HOST_UID = os.getuid()
HOST_GID = os.getgid()
USER_STRING = f"{HOST_UID}:{HOST_GID}"
AGENT_CONFIG = "agent-config.yaml"


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
        ["docker", "buildx", "build", "-f", "Dockerfile", 
            "--build-arg", f"USER_ID={HOST_UID}",
            "--build-arg", f"GROUP_ID={HOST_GID}",
            "-t", IMAGE_NAME, "."],
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
    config_path = os.path.join(project_dir, AGENT_CONFIG)

    if not os.path.exists(config_path):
        print(f"❌ Error: No agent-config.yaml found at {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print(f"❌ Error: Expected a YAML mapping in {config_path}")
        sys.exit(1)


    # Retrieve custom provider for OPENAI_BASE_URL
    active_provider = config.get("active_provider", "openai")
    provider_config = config.get("providers", {}).get(active_provider, {})
    host = provider_config.get("host", "http://127.0.0.1:1234/v1")

    print(f"🚀 Launching Goose with provider: {config.get('active_provider', 'Unknown')}")

    # Generate a temporary config file inside a local temp dir to mount into the container
    container_config_dir = os.path.expanduser("~/.config/goose")
    os.makedirs(container_config_dir, exist_ok=True)

    app_config_path = os.path.join(container_config_dir, "config.yaml")
    shutil.copyfile(config_path, app_config_path)

    ensure_docker_image()

    # Build the Docker command with unprivileged security flags
    docker_cmd = [
        "docker", "run", "-it", "--rm",
        "--add-host", f"qwen-server:192.168.178.50",
        "--user", USER_STRING,
        "--add-host", "host.docker.internal:host-gateway",
        # "--security-opt", "no-new-privileges=true",
        "-v", f"{project_dir}:/workspace",
        "-v", f"{container_config_dir}:/home/goose/.config/goose",
        "-e", f"OPENAI_BASE_URL={host}",
        IMAGE_NAME,
        "goose", "session"
    ]

    subprocess.run(docker_cmd)

if __name__ == "__main__":
    main()