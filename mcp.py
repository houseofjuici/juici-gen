from typing import Any, Dict, Optional, Sequence
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import Resource, ResourceManager
from mcp.server.fastmcp.tools import ToolManager
from mcp.server.fastmcp.prompts import PromptManager
from mcp.types import TextContent, ImageContent, EmbeddedResource
import os
import aiohttp
import json

class MCPManager:
    def __init__(self, name: str = "JuiciGenAgent", instructions: Optional[str] = None):
        """Initialize the MCP manager with FastMCP server."""
        self.fastmcp = FastMCP(
            name=name,
            instructions=instructions,
            debug=os.getenv("DEBUG", "false").lower() == "true"
        )
        
        # Initialize managers
        self._tool_manager = ToolManager()
        self._resource_manager = ResourceManager()
        self._prompt_manager = PromptManager()
        
        # Set up default tools and resources
        self._setup_default_tools()
        self._setup_default_resources()
        self._setup_available_mcps()
    
    def _setup_default_tools(self):
        """Set up default tools for the MCP server."""
        @self.fastmcp.tool(
            name="get_model_info",
            description="Get information about available models",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Name of the model to get info for"
                    }
                }
            }
        )
        async def get_model_info(model_name: Optional[str] = None) -> Sequence[TextContent]:
            """Get information about available models."""
            models = self._resource_manager.list_resources("models")
            if model_name:
                model = next((m for m in models if m.name == model_name), None)
                if model:
                    return [TextContent(text=str(model))]
                return [TextContent(text=f"Model {model_name} not found")]
            return [TextContent(text=str(models))]
    
    def _setup_default_resources(self):
        """Set up default resources for the MCP server."""
        # Add OpenAI models as resources
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self._resource_manager.add_resource(
                Resource(
                    name="gpt-4",
                    type="model",
                    content={"api_key": openai_api_key, "model": "gpt-4"}
                )
            )
            self._resource_manager.add_resource(
                Resource(
                    name="gpt-3.5-turbo",
                    type="model",
                    content={"api_key": openai_api_key, "model": "gpt-3.5-turbo"}
                )
            )
    
    def _setup_available_mcps(self):
        """Set up available MCPs based on environment variables."""
        # Anthropic MCP
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self._resource_manager.add_resource(
                Resource(
                    name="claude-3",
                    type="model",
                    content={"api_key": anthropic_key, "model": "anthropic/claude-3-7-sonnet-20250219"}
                )
            )
        
        # Google Gemini MCP
        gemini_key = os.getenv("GEMINI_AI_KEY")
        if gemini_key:
            self._resource_manager.add_resource(
                Resource(
                    name="gemini",
                    type="model",
                    content={"api_key": gemini_key, "model": "gemini/gemini-2.5-pro-exp-03-25"}
                )
            )
        
        # Groq MCP
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self._resource_manager.add_resource(
                Resource(
                    name="groq",
                    type="model",
                    content={"api_key": groq_key, "model": "groq/llama-3.2-90b-vision-preview"}
                )
            )
        
        # xAI MCP
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            self._resource_manager.add_resource(
                Resource(
                    name="grok",
                    type="model",
                    content={"api_key": xai_key, "model": "xai/grok-2-latest"}
                )
            )
        
        # GitHub MCP
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.add_tool(
                name="github_search",
                func=self._github_search,
                description="Search GitHub repositories and code",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "type": {
                            "type": "string",
                            "description": "Search type (repositories, code, issues, etc.)",
                            "enum": ["repositories", "code", "issues", "users"]
                        }
                    }
                }
            )
        
        # Google Maps MCP
        maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if maps_key:
            self.add_tool(
                name="maps_search",
                func=self._maps_search,
                description="Search locations using Google Maps",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Location search query"
                        },
                        "type": {
                            "type": "string",
                            "description": "Search type (places, directions, geocode)",
                            "enum": ["places", "directions", "geocode"]
                        }
                    }
                }
            )
    
    async def _github_search(self, query: str, type: str = "repositories") -> Sequence[TextContent]:
        """Search GitHub using the GitHub API."""
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return [TextContent(text="GitHub token not found")]
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.github.com/search/{type}?q={query}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    for item in data.get("items", [])[:5]:  # Limit to top 5 results
                        if type == "repositories":
                            results.append(f"Repo: {item['full_name']} - {item['description']}")
                        elif type == "code":
                            results.append(f"File: {item['name']} in {item['repository']['full_name']}")
                        elif type == "issues":
                            results.append(f"Issue: {item['title']} in {item['repository']['full_name']}")
                        elif type == "users":
                            results.append(f"User: {item['login']} - {item['bio']}")
                    return [TextContent(text="\n".join(results))]
                else:
                    return [TextContent(text=f"GitHub API error: {response.status}")]
    
    async def _maps_search(self, query: str, type: str = "places") -> Sequence[TextContent]:
        """Search Google Maps using the Maps API."""
        maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not maps_key:
            return [TextContent(text="Google Maps API key not found")]
        
        async with aiohttp.ClientSession() as session:
            if type == "places":
                url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={maps_key}"
            elif type == "geocode":
                url = f"https://maps.googleapis.com/maps/api/geocode/json?address={query}&key={maps_key}"
            else:
                return [TextContent(text=f"Unsupported search type: {type}")]
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    if type == "places":
                        for place in data.get("results", [])[:5]:  # Limit to top 5 results
                            results.append(f"Place: {place['name']} - {place.get('formatted_address', 'No address')}")
                    elif type == "geocode":
                        for result in data.get("results", [])[:5]:
                            results.append(f"Location: {result['formatted_address']}")
                    return [TextContent(text="\n".join(results))]
                else:
                    return [TextContent(text=f"Google Maps API error: {response.status}")]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Call a tool by name with arguments."""
        return await self.fastmcp.call_tool(name, arguments)
    
    def add_tool(self, name: str, func: callable, description: str, input_schema: Dict[str, Any]):
        """Add a new tool to the MCP server."""
        @self.fastmcp.tool(
            name=name,
            description=description,
            inputSchema=input_schema
        )
        async def tool_wrapper(**kwargs):
            return await func(**kwargs)
    
    def add_resource(self, name: str, resource_type: str, content: Dict[str, Any]):
        """Add a new resource to the MCP server."""
        self._resource_manager.add_resource(
            Resource(
                name=name,
                type=resource_type,
                content=content
            )
        )
    
    def add_prompt(self, name: str, template: str, variables: Dict[str, Any]):
        """Add a new prompt template to the MCP server."""
        self._prompt_manager.add_prompt(
            name=name,
            template=template,
            variables=variables
        )
    
    def run(self, transport: str = "sse"):
        """Run the MCP server."""
        self.fastmcp.run(transport=transport)
    
    def get_fastapi_app(self) -> FastAPI:
        """Get the FastAPI application for the MCP server."""
        return self.fastmcp.get_fastapi_app() 