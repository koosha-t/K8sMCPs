# Multi-stage Dockerfile to create an HTTP-enabled GitHub MCP Server
# Stage 1: Get the official GitHub MCP server binary
FROM ghcr.io/github/github-mcp-server:latest AS mcp-server

# Stage 2: Build the final image with Node.js + Supergateway
FROM node:20-alpine

# Metadata
LABEL maintainer="K8sMCPs"
LABEL description="GitHub MCP Server with HTTP/SSE support via Supergateway"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy GitHub MCP server binary from official image
COPY --from=mcp-server /server/github-mcp-server /usr/local/bin/github-mcp-server

# Ensure the binary is executable
RUN chmod +x /usr/local/bin/github-mcp-server

# Install supergateway globally
RUN npm install -g supergateway

# Create non-root user for security
# Use the existing node user (uid/gid 1000) from the base image
RUN chown -R node:node /app

# Switch to non-root user
USER node

# Expose HTTP port for Supergateway
EXPOSE 8080

# Health check endpoint (Supergateway provides SSE endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/sse || exit 1

# Run Supergateway wrapping the GitHub MCP server
# Supergateway will:
# - Spawn github-mcp-server stdio as a child process
# - Expose it via HTTP/SSE on port 8080
# - Handle stdio <-> HTTP translation
CMD ["supergateway", \
     "--stdio", "github-mcp-server stdio", \
     "--port", "8080", \
     "--ssePath", "/sse", \
     "--messagePath", "/message"]
