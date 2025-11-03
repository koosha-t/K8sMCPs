# GitHub MCP Server - Kubernetes Deployment

Official GitHub MCP server deployed on Kubernetes, enabling AI agents to interact with GitHub repositories, issues, pull requests, and workflows.

## Overview

The GitHub MCP Server provides programmatic access to GitHub through the Model Context Protocol (MCP). It runs in Kubernetes using Supergateway to expose the stdio-based server via Streamable HTTP transport.

**Key Features:**
- Repository management (browse, search, analyze)
- Issues and pull requests
- GitHub Actions workflows
- Code security and scanning
- Team collaboration

## Prerequisites

Verify you have these installed:

```bash
# Docker
docker --version

# Kind
kind version

# Kubectl
kubectl version --client

# Make
make --version
```

**Required:**
- Docker Desktop running
- Kind (Kubernetes in Docker)
- kubectl configured
- GitHub Personal Access Token with scopes: `repo`, `read:packages`, `read:org`, `workflow`

## Quick Start

### 1. Configure Environment

```bash
cp .env.template .env
# Edit .env and set your GITHUB_TOKEN
```

### 2. Deploy Everything

```bash
# Creates kind cluster, builds image, deploys server
make dev-deploy-full
```

This single command:
- Starts local Docker registry
- Creates kind cluster with registry support
- Builds and pushes the Docker image
- Deploys GitHub MCP server to the cluster

### 3. Verify Deployment

```bash
make verify
make logs
```

Server is deployed and accessible within the cluster at:
- `http://github-mcp-server.mcp-servers.svc.cluster.local:8080`

## Make Commands

**Full Deployment:**
```bash
make dev-deploy-full    # Complete setup: registry + cluster + build + deploy
```

**Individual Steps:**
```bash
make registry-up        # Start local Docker registry
make kind-up            # Create kind cluster
make build-push         # Build and push image
make deploy             # Deploy to cluster
```

**Management:**
```bash
make verify             # Check deployment status
make logs               # View server logs
make restart            # Restart deployment
make clean              # Delete all resources
```

**Cleanup:**
```bash
make kind-down          # Delete kind cluster
make registry-down      # Stop local registry
```

## AKS Deployment

```bash
# Set kubectl context and deploy everything
kubectl config use-context <your-aks-cluster>
make aks-deploy-full

# Then use existing commands
make verify
make logs
```

## Using the Server

**In-cluster URL:**
```
http://github-mcp-server.mcp-servers.svc.cluster.local:8080/mcp
```

## Testing with an Agent

See the [test agent](../test-agents/github_test_agent/) which demonstrates how an agent can connect to the MCP server and make calls to it. 

## Configuration

Edit `configmap.yaml` to customize:

```yaml
GITHUB_TOOLSETS: "default,actions,code_security"  # Enable specific features
GITHUB_READ_ONLY: "1"                              # Read-only mode
```

After changes:
```bash
make update-config
```
