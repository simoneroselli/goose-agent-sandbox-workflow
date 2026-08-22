# Jagent

An experimental workflow for constraining an AI coding agent within a securely configured container.

![Big Picture](doc/src/big_pic.jpeg)

## Colima

Jagent uses [Colima](https://github.com/abiosoft/colima) instead of Docker Desktop. This is a deliberate local-development choice: Colima simplifies networking when the LLM is running on a separate host on the LAN. This project does not claim that Colima provides stronger isolation than Docker Desktop; the choice is primarily about connectivity and workflow simplicity.

## Successful Goose Prompt

![Jagent logo](doc/src/logo.png)

Example of a successful prompt inside the configured project boundary:

```text
You: Inspect the project files and summarize the current implementation. Do not modify anything.

Goose: I inspected the mounted project directory and found the launcher, container definition,
	   and configuration template. No files were modified.
```

See [Current Scope](doc/current-scope.md) for the implementation boundary and open questions.

This project explores how to make an AI coding agent, currently **Qwen 3.8**, behave within clear container boundaries. It is a small, experimental harness around the Goose CLI rather than a general-purpose container platform.

The central question is how to balance two kinds of control:

- **Strong sandboxing:** run without root privileges or setuid behavior, prevent privilege escalation, and expose only the intended working directory.
- **Agent configuration:** limit what the agent can do, avoid unrestricted shell access, and require manual approval before changes or other sensitive actions.

The goal is defense in depth. Container isolation limits the impact of a misbehaving agent, while Goose configuration limits the actions the agent is allowed to request. Neither layer should be treated as a complete security boundary on its own.

## Configuration

Each Goose project should contain an `agent-config.yaml` file at its project root. Start with the template:

```bash
cp templates/agent-config.yaml.template /path/to/your-project/agent-config.yaml
```

Review the provider, model, endpoint, approval mode, and enabled extensions before launching an agent. Keep manual approval enabled while evaluating agent behavior.

## Usage

From this repository, pass exactly one project directory to the launcher:

```bash
python3 run-agent.py /path/to/your-project
```

The project directory must contain `agent-config.yaml`. The launcher builds the image if necessary and then starts an interactive Goose session inside the container.
