# Goose Agent Sandbox Workflow

This project explores how to make an AI coding agent, currently Qwen 3.8, behave within clear container boundaries. It is a small, experimental harness around the Goose CLI rather than a general-purpose container platform.

The central question is how to balance two kinds of control:

- **Strong sandboxing:** run without root privileges or setuid behavior, prevent privilege escalation, and expose only the intended working directory.
- **Agent configuration:** limit what the agent can do, avoid unrestricted shell access, and require manual approval before changes or other sensitive actions.

The goal is defense in depth. Container isolation limits the impact of a misbehaving agent, while Goose configuration limits the actions the agent is allowed to request. Neither layer should be treated as a complete security boundary on its own.

## Current Scope

The workflow currently:

- Builds `goose-sandbox:latest` from the repository `Dockerfile` when the image is missing.
- Runs Goose in an Ubuntu container as a non-root user.
- Mounts the selected project directory at `/workspace` and sets it as Goose's working directory.
- Uses Docker's `no-new-privileges` security option.
- Passes the provider, model, endpoint, approval mode, and developer-extension setting from `agent-config.yaml`.
- Generates and mounts a minimal Goose application configuration for the container.

The project is intentionally focused on the boundary between the agent and its execution environment. It does not claim to provide a complete security assessment of Docker, the host operating system, the model, Goose, or the configured API endpoint.

## Configuration

Each Goose project should contain an `agent-config.yaml` file at its project root. Start with the template:

```bash
cp config/agent-config.yaml.template /path/to/your-project/agent-config.yaml
```

Review the provider, model, endpoint, approval mode, and enabled extensions before launching an agent. Keep manual approval enabled while evaluating agent behavior.

## Usage

From this repository, pass exactly one project directory to the launcher:

```bash
python3 run-agent.py /path/to/your-project
```

The project directory must contain `agent-config.yaml`. The launcher builds the image if necessary and then starts an interactive Goose session inside the container.

## Open Questions

This experiment is intended to make trade-offs visible. Areas for further work include:

- defining a reliable no-shell or restricted-tool policy for the agent;
- reducing the container's filesystem, network, and device access;
- aligning container and host-user IDs without weakening file permissions;
- documenting which actions require approval and which are blocked outright.
- boundary-escape scenarios;