.PHONY: help deploy verify logs port-forward status restart update-config update-secret clean kind-up kind-down kind-status dev-deploy registry-up registry-down registry-status build push build-push dev-deploy-full

# Default target
.DEFAULT_GOAL := help

# Load environment variables from .env file
ifneq (,$(wildcard .env))
include .env
export
endif

# Default values
NAMESPACE ?= mcp-servers
GITHUB_TOOLSETS ?= default,actions,code_security
KIND_CLUSTER_NAME ?= mcp-dev

# Docker registry configuration
REGISTRY_NAME ?= kind-registry
REGISTRY_PORT ?= 5001
IMAGE_NAME ?= github-mcp-server
IMAGE_TAG ?= latest
IMAGE_FULL_NAME := localhost:$(REGISTRY_PORT)/$(IMAGE_NAME):$(IMAGE_TAG)

help: ## Show this help message
	@echo "GitHub MCP Server - Kubernetes Deployment"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Deployment Targets:"
	@grep -E '^(deploy|verify|logs|port-forward|status|restart|update-config|update-secret|clean):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Local Development (Kind + Registry):"
	@grep -E '^(registry-up|registry-down|registry-status|build|push|build-push|kind-up|kind-down|kind-status|dev-deploy|dev-deploy-full):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start (Local Dev):"
	@echo "  1. cp .env.template .env  # Configure environment"
	@echo "  2. make registry-up       # Start local registry"
	@echo "  3. make kind-up           # Create kind cluster"
	@echo "  4. make build-push        # Build and push image"
	@echo "  5. make deploy            # Deploy to cluster"
	@echo "  6. make port-forward      # Access at localhost:8080"
	@echo ""
	@echo "Or use: make dev-deploy-full (does steps 2-5 automatically)"
	@echo ""

deploy: check-env ## Deploy the GitHub MCP server (namespace, secret, configmap, deployment, service)
	@echo "Deploying GitHub MCP Server..."
	@kubectl apply -f namespace.yaml
	@echo "Creating secret from .env file..."
	@kubectl create secret generic github-mcp-token \
		--namespace=$(NAMESPACE) \
		--from-literal=token=$(GITHUB_TOKEN) \
		--dry-run=client -o yaml | kubectl apply -f -
	@echo "Applying manifests..."
	@kubectl apply -f configmap.yaml
	@kubectl apply -f deployment.yaml
	@kubectl apply -f service.yaml
	@echo ""
	@echo "Deployment complete! Run 'make verify' to check status."

verify: ## Verify deployment status and show pod information
	@echo "Checking deployment status..."
	@echo ""
	@echo "=== Namespace ==="
	@kubectl get namespace $(NAMESPACE) 2>/dev/null || echo "Namespace not found"
	@echo ""
	@echo "=== Deployment ==="
	@kubectl get deployment -n $(NAMESPACE) github-mcp-server 2>/dev/null || echo "Deployment not found"
	@echo ""
	@echo "=== Pods ==="
	@kubectl get pods -n $(NAMESPACE) -l app.kubernetes.io/name=github-mcp-server 2>/dev/null || echo "No pods found"
	@echo ""
	@echo "=== Service ==="
	@kubectl get svc -n $(NAMESPACE) github-mcp-server 2>/dev/null || echo "Service not found"
	@echo ""
	@echo "=== Recent Events ==="
	@kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp' 2>/dev/null | tail -5 || echo "No events found"

logs: ## View server logs (follow mode)
	@echo "Streaming logs from GitHub MCP Server..."
	@kubectl logs -n $(NAMESPACE) -l app.kubernetes.io/name=github-mcp-server -f

port-forward: ## Set up port forwarding to access the server locally (localhost:8080)
	@echo "Setting up port forwarding to localhost:8080..."
	@echo "Press Ctrl+C to stop"
	@kubectl port-forward -n $(NAMESPACE) svc/github-mcp-server 8080:8080

status: ## Show all resources in the namespace
	@echo "GitHub MCP Server Resources:"
	@echo ""
	@kubectl get all -n $(NAMESPACE) 2>/dev/null || echo "No resources found in namespace $(NAMESPACE)"

restart: ## Restart the deployment
	@echo "Restarting GitHub MCP Server deployment..."
	@kubectl rollout restart deployment/github-mcp-server -n $(NAMESPACE)
	@echo "Waiting for rollout to complete..."
	@kubectl rollout status deployment/github-mcp-server -n $(NAMESPACE)

update-config: check-env ## Update configmap and restart deployment
	@echo "Updating ConfigMap..."
	@kubectl apply -f configmap.yaml
	@echo "Restarting deployment to pick up changes..."
	@kubectl rollout restart deployment/github-mcp-server -n $(NAMESPACE)
	@kubectl rollout status deployment/github-mcp-server -n $(NAMESPACE)

update-secret: check-env ## Update secret and restart deployment
	@echo "Updating secret from .env file..."
	@kubectl create secret generic github-mcp-token \
		--namespace=$(NAMESPACE) \
		--from-literal=token=$(GITHUB_TOKEN) \
		--dry-run=client -o yaml | kubectl apply -f -
	@echo "Restarting deployment to pick up changes..."
	@kubectl rollout restart deployment/github-mcp-server -n $(NAMESPACE)
	@kubectl rollout status deployment/github-mcp-server -n $(NAMESPACE)

clean: ## Delete all resources (namespace, deployment, service, configmap, secret)
	@echo "WARNING: This will delete all GitHub MCP Server resources!"
	@echo "Press Ctrl+C within 5 seconds to cancel..."
	@sleep 5
	@echo "Deleting resources..."
	@kubectl delete -f service.yaml 2>/dev/null || true
	@kubectl delete -f deployment.yaml 2>/dev/null || true
	@kubectl delete -f configmap.yaml 2>/dev/null || true
	@kubectl delete secret github-mcp-token -n $(NAMESPACE) 2>/dev/null || true
	@echo ""
	@echo "Resources deleted. Namespace '$(NAMESPACE)' preserved."
	@echo "To delete the namespace, run: kubectl delete namespace $(NAMESPACE)"

check-env: ## Check if .env file exists and required variables are set
	@if [ ! -f .env ]; then \
		echo "ERROR: .env file not found!"; \
		echo ""; \
		echo "Please create .env from the template:"; \
		echo "  cp .env.template .env"; \
		echo ""; \
		echo "Then edit .env and set your GITHUB_TOKEN"; \
		exit 1; \
	fi
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "ERROR: GITHUB_TOKEN is not set in .env file!"; \
		echo ""; \
		echo "Please edit .env and set your GitHub Personal Access Token"; \
		exit 1; \
	fi
	@echo "Environment check passed ✓"

# ==============================================================================
# Local Development with Kind
# ==============================================================================

kind-up: ## Create a local kind cluster for development
	@echo "Checking if kind is installed..."
	@if ! command -v kind >/dev/null 2>&1; then \
		echo "ERROR: kind is not installed!"; \
		echo ""; \
		echo "Install kind:"; \
		echo "  macOS:   brew install kind"; \
		echo "  Linux:   https://kind.sigs.k8s.io/docs/user/quick-start/#installation"; \
		echo "  Windows: choco install kind"; \
		exit 1; \
	fi
	@echo "Checking if cluster '$(KIND_CLUSTER_NAME)' already exists..."
	@if kind get clusters 2>/dev/null | grep -q "^$(KIND_CLUSTER_NAME)$$"; then \
		echo "Cluster '$(KIND_CLUSTER_NAME)' already exists."; \
		echo "Switching kubectl context..."; \
		kubectl config use-context kind-$(KIND_CLUSTER_NAME); \
	else \
		echo "Creating kind cluster with containerd registry config..."; \
		kind create cluster --name $(KIND_CLUSTER_NAME) --config=kind-config.yaml; \
		echo ""; \
		echo "Cluster created successfully!"; \
		echo ""; \
		echo "Connecting cluster to local registry..."; \
		if [ "$$(docker ps -q -f name=$(REGISTRY_NAME))" ]; then \
			docker network connect kind $(REGISTRY_NAME) 2>/dev/null || true; \
			echo "Configuring registry on all nodes..."; \
			for node in $$(kind get nodes --name $(KIND_CLUSTER_NAME)); do \
				docker exec "$$node" mkdir -p "/etc/containerd/certs.d/localhost:$(REGISTRY_PORT)"; \
				echo '[host."http://$(REGISTRY_NAME):5000"]' | docker exec -i "$$node" tee /etc/containerd/certs.d/localhost:$(REGISTRY_PORT)/hosts.toml > /dev/null; \
			done; \
			kubectl apply -f local-registry-configmap.yaml; \
			echo "✓ Cluster configured to use local registry at localhost:$(REGISTRY_PORT)"; \
		else \
			echo "⚠ Local registry not running. Run 'make registry-up' first."; \
		fi; \
	fi
	@echo ""
	@echo "✓ Kind cluster '$(KIND_CLUSTER_NAME)' is ready"
	@echo "✓ kubectl context set to: kind-$(KIND_CLUSTER_NAME)"
	@echo ""
	@echo "Next steps:"
	@echo "  make build-push   # Build and push image"
	@echo "  make deploy       # Deploy GitHub MCP server"
	@echo "  make port-forward # Access at localhost:8080"

kind-down: ## Delete the local kind cluster
	@echo "Checking if cluster '$(KIND_CLUSTER_NAME)' exists..."
	@if kind get clusters 2>/dev/null | grep -q "^$(KIND_CLUSTER_NAME)$$"; then \
		echo "Deleting kind cluster '$(KIND_CLUSTER_NAME)'..."; \
		kind delete cluster --name $(KIND_CLUSTER_NAME); \
		echo ""; \
		echo "✓ Cluster '$(KIND_CLUSTER_NAME)' deleted successfully"; \
	else \
		echo "Cluster '$(KIND_CLUSTER_NAME)' does not exist."; \
	fi

kind-status: ## Show kind cluster status and current kubectl context
	@echo "=== Kind Clusters ==="
	@if command -v kind >/dev/null 2>&1; then \
		if kind get clusters 2>/dev/null | grep -q .; then \
			kind get clusters; \
		else \
			echo "No kind clusters found"; \
		fi; \
	else \
		echo "kind is not installed"; \
	fi
	@echo ""
	@echo "=== Current kubectl Context ==="
	@kubectl config current-context 2>/dev/null || echo "No context set"
	@echo ""
	@echo "=== Cluster Info ==="
	@kubectl cluster-info 2>/dev/null || echo "Not connected to a cluster"

dev-deploy: kind-up deploy ## Create kind cluster and deploy in one command
	@echo ""
	@echo "=========================================="
	@echo "Local development environment ready!"
	@echo "=========================================="
	@echo ""
	@echo "Run 'make port-forward' to access the server at localhost:8080"

# ==============================================================================
# Local Docker Registry
# ==============================================================================

registry-up: ## Start local Docker registry for Kind
	@echo "Checking if registry '$(REGISTRY_NAME)' is running..."
	@if [ "$$(docker ps -q -f name=$(REGISTRY_NAME))" ]; then \
		echo "Registry '$(REGISTRY_NAME)' is already running."; \
	else \
		if [ "$$(docker ps -aq -f name=$(REGISTRY_NAME))" ]; then \
			echo "Starting existing registry container..."; \
			docker start $(REGISTRY_NAME); \
		else \
			echo "Creating new registry container..."; \
			docker run -d --restart=always -p $(REGISTRY_PORT):5000 --name $(REGISTRY_NAME) registry:2; \
		fi; \
		echo ""; \
		echo "✓ Registry is running at localhost:$(REGISTRY_PORT)"; \
	fi

registry-down: ## Stop local Docker registry
	@echo "Stopping registry '$(REGISTRY_NAME)'..."
	@if [ "$$(docker ps -q -f name=$(REGISTRY_NAME))" ]; then \
		docker stop $(REGISTRY_NAME); \
		echo "✓ Registry stopped"; \
	else \
		echo "Registry '$(REGISTRY_NAME)' is not running"; \
	fi

registry-status: ## Show registry status
	@echo "=== Registry Status ==="
	@if [ "$$(docker ps -q -f name=$(REGISTRY_NAME))" ]; then \
		echo "Status: Running"; \
		echo "Port: $(REGISTRY_PORT)"; \
		echo "URL: localhost:$(REGISTRY_PORT)"; \
		echo ""; \
		echo "Images in registry:"; \
		curl -s http://localhost:$(REGISTRY_PORT)/v2/_catalog 2>/dev/null || echo "Unable to connect"; \
	else \
		echo "Status: Not running"; \
	fi

# ==============================================================================
# Docker Build & Push
# ==============================================================================

build: ## Build Docker image
	@echo "Building Docker image: $(IMAGE_FULL_NAME)"
	@docker build -t $(IMAGE_FULL_NAME) .
	@echo ""
	@echo "✓ Image built successfully"
	@echo "  Image: $(IMAGE_FULL_NAME)"

push: ## Push Docker image to local registry
	@echo "Pushing image to local registry..."
	@if ! [ "$$(docker ps -q -f name=$(REGISTRY_NAME))" ]; then \
		echo "ERROR: Registry is not running!"; \
		echo "Run 'make registry-up' first"; \
		exit 1; \
	fi
	@docker push $(IMAGE_FULL_NAME)
	@echo ""
	@echo "✓ Image pushed successfully"
	@echo "  Registry: localhost:$(REGISTRY_PORT)"
	@echo "  Image: $(IMAGE_NAME):$(IMAGE_TAG)"

build-push: build push ## Build and push Docker image

# ==============================================================================
# Complete Local Development Setup
# ==============================================================================

dev-deploy-full: registry-up kind-up build-push deploy ## Complete setup: registry + kind + build + deploy
	@echo ""
	@echo "=========================================="
	@echo "Complete development environment ready!"
	@echo "=========================================="
	@echo ""
	@echo "✓ Local registry running"
	@echo "✓ Kind cluster running"
	@echo "✓ Image built and pushed"
	@echo "✓ GitHub MCP Server deployed"
	@echo ""
	@echo "Next: make port-forward  # Access at localhost:8080"
