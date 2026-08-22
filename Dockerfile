FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    bash \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user named 'agentuser' with UID 1000
RUN useradd -m agentuser && \
    mkdir -p /workspace && \
    chown -R agentuser:agentuser /workspace

# Switch to the non-root user for all subsequent commands and execution
USER agentuser
WORKDIR /home/agentuser

# Download and install Goose CLI explicitly pinning the stable script
RUN curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh -o download_cli.sh && \
    CONFIGURE=false bash download_cli.sh

# Add goose binary to PATH
ENV PATH="/home/agentuser/.local/bin:${PATH}"

WORKDIR /workspace

CMD ["bash"]