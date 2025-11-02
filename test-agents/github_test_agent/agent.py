"""
ADK Agent for GitHub MCP Server Testing

This agent connects to the GitHub MCP server to test repository operations,
issue management, pull requests, and GitHub Actions workflows.

Note: The GitHub MCP server uses Supergateway which wraps the stdio-based
MCP server with HTTP/SSE transport. Therefore, we use SseConnectionParams
instead of StreamableHTTPConnectionParams (which is for FastMCP servers).
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
# Supergateway exposes SSE endpoint at /sse
GITHUB_MCP_URL = os.getenv("GITHUB_MCP_SERVER_URL", "http://localhost:8080/sse")

# Validate required configuration
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is required. Please set it in your .env file.\n"
        "Copy .env.template to .env and add your OpenAI API key."
    )

# Create the GitHub test agent
root_agent = LlmAgent(
    # Configure LLM using LiteLLM with OpenAI
    model=LiteLlm(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        max_tokens=10000,
    ),

    # Agent metadata
    name="github_test_agent",
    description="Test agent for GitHub MCP server operations including repositories, issues, PRs, and workflows",

    # Agent system instructions
    instruction=(
        "You are a GitHub repository assistant that helps users interact with GitHub repositories "
        "through the GitHub MCP server.\n\n"

        "Your capabilities:\n"
        "1. **Repository Operations**:\n"
        "   - Search for repositories by topic, language, stars, or keywords\n"
        "   - Get detailed repository information (description, stars, forks, etc.)\n"
        "   - Browse repository contents and file structure\n"
        "   - Analyze commits and commit history\n"
        "   - View and analyze README files\n\n"

        "2. **Issue Management**:\n"
        "   - List issues with filters (state, labels, assignees)\n"
        "   - Get detailed issue information\n"
        "   - Create new issues (if not in read-only mode)\n"
        "   - Update and comment on issues\n"
        "   - Analyze issue trends and patterns\n\n"

        "3. **Pull Request Operations**:\n"
        "   - List pull requests with various filters\n"
        "   - Get PR details including reviews and checks\n"
        "   - Analyze PR activity and merge status\n"
        "   - Review PR diffs and changes\n\n"

        "4. **GitHub Actions & CI/CD**:\n"
        "   - List workflow runs and their status\n"
        "   - Analyze workflow failures and logs\n"
        "   - Monitor CI/CD pipeline health\n"
        "   - Identify build and test issues\n\n"

        "5. **Code Security**:\n"
        "   - View security alerts and findings\n"
        "   - Analyze Dependabot alerts\n"
        "   - Review code scanning results\n"
        "   - Check for security advisories\n\n"

        "**Best Practices**:\n"
        "- Always provide clear, well-formatted responses with relevant details\n"
        "- When showing lists, organize information in a readable format\n"
        "- For errors or failures, provide context and suggest next steps\n"
        "- When analyzing repositories, consider multiple aspects (code quality, activity, community)\n"
        "- Use markdown formatting for better readability\n"
        "- When appropriate, provide links to GitHub resources\n\n"

        "**Response Format**:\n"
        "- Use bullet points for lists\n"
        "- Use code blocks for file contents or code snippets\n"
        "- Use tables for comparing multiple items\n"
        "- Include relevant metrics (stars, forks, open issues, etc.)\n"
        "- Highlight important information or warnings\n\n"

        "You are designed to help test and validate the GitHub MCP server functionality, "
        "so be thorough in your responses and surface any issues or limitations you encounter."
    ),

    # Connect to GitHub MCP server via Supergateway (SSE transport)
    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url=GITHUB_MCP_URL
            )
        )
    ]
)

# Print configuration on import (helpful for debugging)
if __name__ != "__main__":
    print(f"GitHub Test Agent initialized")
    print(f"  Model: {OPENAI_MODEL}")
    print(f"  MCP Server: {GITHUB_MCP_URL}")
