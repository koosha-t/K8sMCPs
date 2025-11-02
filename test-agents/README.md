# Test Agents for K8s MCP Servers

Test agents built with Google's Agent Development Kit (ADK) for testing MCP servers deployed on Kubernetes.

## Overview

This directory contains ADK-based test agents that connect to MCP servers running in your Kubernetes cluster. The agents use port-forwarding to communicate with the MCP servers and provide an interactive web interface for testing.

## Quick Start

### 1. Deploy GitHub MCP Server

```bash
cd ../github-mcp-server
make dev-deploy-full
make port-forward
```

### 2. Run Test Agent

```bash
uv sync --directory test-agents #run this from the root dir
cd test-agents
source .venv/bin/activate
cp .env.template .env #set your open ai token in the .env file
adk web --port 9000
```
Open your browser

```
http://localhost:9000
```
Select your agent and start testing!

