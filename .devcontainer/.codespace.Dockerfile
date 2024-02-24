FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# Install Podman CLI
RUN apt-get update \
  && apt-get install -y podman
