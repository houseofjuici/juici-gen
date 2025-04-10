from praisonai.tools import BrowserTool, SearchTool, CalculatorTool, FileReaderTool, TerminalTool, JSONExplorerTool, CodeInterpreterTool
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from playwright.async_api import async_playwright
import asyncio
from embassai import EmbassaiClient
import requests
import json
import os

def get_tools():
    return [
        BrowserTool(),
        SearchTool(),
        CalculatorTool(),
        FileReaderTool(),
        TerminalTool(),
        JSONExplorerTool(),
        CodeInterpreterTool(),
    ]

class WebInteractionTool(BaseTool):
    name = "WebInteractionTool"
    description = "Tool for web browsing, data extraction, and form interaction"
    
    async def _run(self, url: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            
            if action == "extract":
                content = await page.content()
                return {"content": content}
            elif action == "fill_form":
                for field, value in data.items():
                    await page.fill(field, value)
                return {"status": "form_filled"}
            elif action == "click":
                await page.click(data["selector"])
                return {"status": "clicked"}
            
            await browser.close()

class WorkflowTool(BaseTool):
    name = "WorkflowTool"
    description = "Tool for creating and managing automation workflows"
    
    def _run(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement workflow creation and management
        return {"workflow": workflow_data}

class WritingTool(BaseTool):
    name = "WritingTool"
    description = "Tool for content generation and research"
    
    def _run(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Implement content generation and research
        return {"content": "Generated content"}

class SecurityTool(BaseTool):
    name = "SecurityTool"
    description = "Tool for secure communications and data handling"
    
    def __init__(self):
        self.embassai = EmbassaiClient()
    
    def _run(self, data: Dict[str, Any], action: str) -> Dict[str, Any]:
        if action == "encrypt":
            return self.embassai.encrypt(data)
        elif action == "decrypt":
            return self.embassai.decrypt(data)
        return {"error": "Invalid action"}

class ReviewTool(BaseTool):
    name = "ReviewTool"
    description = "Tool for reviewing and optimizing tasks"
    
    def _run(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement review and optimization logic
        return {"recommendations": []}

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information"

    def _run(self, query: str) -> str:
        # This is a placeholder for actual web search implementation
        return f"Search results for: {query}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

class FileSystemTool(BaseTool):
    name = "file_system"
    description = "Interact with the file system"

    def _run(self, operation: str, path: str, content: str = None) -> str:
        try:
            if operation == "read":
                with open(path, 'r') as f:
                    return f.read()
            elif operation == "write":
                with open(path, 'w') as f:
                    f.write(content)
                return "File written successfully"
            elif operation == "delete":
                os.remove(path)
                return "File deleted successfully"
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, operation: str, path: str, content: str = None) -> str:
        return self._run(operation, path, content)

class APITool(BaseTool):
    name = "api"
    description = "Make API requests"

    def _run(self, method: str, url: str, data: Dict[str, Any] = None) -> str:
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    async def _arun(self, method: str, url: str, data: Dict[str, Any] = None) -> str:
        return self._run(method, url, data)

# Register all tools
TOOLS = [
    WebSearchTool(),
    FileSystemTool(),
    APITool()
]

def get_tool_by_name(name: str) -> Optional[BaseTool]:
    """Get a tool by its name."""
    for tool in TOOLS:
        if tool.name == name:
            return tool
    return None

def register_tool(tool: BaseTool):
    """Register a new tool."""
    if not any(t.name == tool.name for t in TOOLS):
        TOOLS.append(tool)
    else:
        raise ValueError(f"Tool with name {tool.name} already exists")

def unregister_tool(name: str):
    """Unregister a tool by name."""
    global TOOLS
    TOOLS = [t for t in TOOLS if t.name != name]