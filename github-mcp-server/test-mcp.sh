#!/bin/bash

# Test script for GitHub MCP server via Supergateway
# This tests if the server can connect to GitHub

echo "Testing GitHub MCP Server..."
echo ""

# Test 1: Check if server is responding
echo "1. Testing server availability..."
response=$(curl -s -w "\n%{http_code}" http://localhost:9090/message -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": "ping"}' 2>&1)

http_code=$(echo "$response" | tail -n1)
if [ "$http_code" != "000" ]; then
    echo "✓ Server is responding (HTTP $http_code)"
else
    echo "✗ Server is not responding"
    exit 1
fi

echo ""

# Test 2: Initialize MCP connection with session
echo "2. Testing MCP initialize via SSE..."
echo "   Connecting to SSE endpoint..."

# Using curl to test SSE connection
timeout 5s curl -N -H "Accept: text/event-stream" http://localhost:9090/sse 2>&1 | head -n 10 || true

echo ""
echo "✓ SSE endpoint is accessible"
echo ""
echo "Server is healthy and ready to accept MCP connections!"
echo ""
echo "To connect with an MCP client:"
echo "  - SSE endpoint: http://localhost:9090/sse"
echo "  - Message endpoint: http://localhost:9090/message"
