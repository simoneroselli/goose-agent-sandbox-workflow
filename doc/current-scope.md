# Current Scope

Jagent explores how to constrain an AI coding agent, currently **Qwen 3.8**, within a container boundary while keeping the workflow usable.

The workflow currently:

- Builds `goose-sandbox:latest` from the repository `Dockerfile` when the image is missing.
- Runs Goose in an Ubuntu container as a non-root user.
- Mounts the selected project directory at `/workspace` and sets it as Goose's working directory.
- Adds the host and LAN LLM endpoints needed by the local setup.
- Passes the project YAML configuration into the container as Goose's application configuration.
- Starts an interactive `goose session` with the selected project's configuration.

The project is intentionally focused on the boundary between the agent and its execution environment. It does not claim to provide a complete security assessment of Docker, Colima, the host operating system, the model, Goose, or the configured API endpoint.

## Open Questions

This experiment is intended to make trade-offs visible. Areas for further work include:

- defining a reliable no-shell or restricted-tool policy for the agent;
- reducing the container's filesystem, network, and device access;
- aligning container and host-user IDs without weakening file permissions;
- documenting which actions require approval and which are blocked outright;
- testing prompt-injection and boundary-escape scenarios.
