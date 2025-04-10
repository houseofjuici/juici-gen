from typing import List, Dict, Optional, Any, Union
from enum import Enum
import os
from .memory import MemoryManager
from .tools import ToolManager
from .security import SecurityManager
from .workflow import WorkflowManager
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.agents import AgentType, initialize_agent
from langchain.tools import BaseTool
from praisonai import Agent
from praisonai_tools import BaseTool
import aiohttp

class Environment(Enum):
    LOCAL = "local"
    VERCEL = "vercel"

class EmbassaiMode(Enum):
    LOCAL = "local"      # Run Embassai locally
    REMOTE = "remote"    # Connect to remote Embassai server
    DISABLED = "disabled" # No encryption

class AgentMode(Enum):
    BROWSE = "browse"
    BUILD = "build"
    WRITE = "write"
    EXECUTE = "execute"
    REVIEW = "review"
    SECURE = "secure"

class JuiciAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mode = "default"
        self.memory = MemoryManager()
        self.tools = ToolManager()
        self.security = SecurityManager()
        self.workflow = WorkflowManager()
        self.environment = self._detect_environment()
        self.embassai_mode = self._detect_embassai_mode()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model=config.get("model", "gpt-4"),
            openai_api_key=config["openai_api_key"]
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize Embassai based on mode
        self.embassai = self._init_embassai()
        
        # Initialize agent with tools
        self.agent = Agent(
            instructions="You are a helpful AI assistant",
            tools=self._get_tools(),
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        )
    
    def _detect_environment(self) -> Environment:
        """Detect if we're running in Vercel or local environment."""
        if os.environ.get("VERCEL") == "1":
            return Environment.VERCEL
        return Environment.LOCAL
    
    def _detect_embassai_mode(self) -> EmbassaiMode:
        """Detect how Embassai should be used."""
        if self.environment == Environment.VERCEL:
            # In Vercel, check if we have a remote Embassai URL
            if os.getenv("EMBASSAI_API_URL"):
                return EmbassaiMode.REMOTE
            return EmbassaiMode.DISABLED
        else:
            # In local environment, check if Embassai CLI is available
            try:
                # Add local embassai-toolkit to PYTHONPATH
                embassai_path = os.path.join(os.getcwd(), "embassai-toolkit")
                if os.path.exists(embassai_path):
                    import sys
                    sys.path.append(embassai_path)
                    import embassai_toolkit
                    return EmbassaiMode.LOCAL
                return EmbassaiMode.DISABLED
            except ImportError:
                return EmbassaiMode.DISABLED
    
    def _init_embassai(self) -> Optional[Union[Dict[str, str], Any]]:
        """Initialize Embassai based on mode."""
        if self.embassai_mode == EmbassaiMode.LOCAL:
            try:
                # Add local embassai-toolkit to PYTHONPATH
                embassai_path = os.path.join(os.getcwd(), "embassai-toolkit")
                if os.path.exists(embassai_path):
                    import sys
                    sys.path.append(embassai_path)
                    from embassai_toolkit import EmbassaiCLI
                    return EmbassaiCLI()
                print("Warning: Embassai toolkit not found in local directory")
                return None
            except ImportError:
                print("Warning: Embassai CLI not available")
                return None
        elif self.embassai_mode == EmbassaiMode.REMOTE:
            # Initialize remote connection
            return {
                "api_url": os.getenv("EMBASSAI_API_URL"),
                "api_key": os.getenv("EMBASSAI_API_KEY"),
                "encryption_key": os.getenv("EMBASSAI_ENCRYPTION_KEY"),
                "room_id": os.getenv("EMBASSAI_ROOM_ID")
            }
        else:
            return None
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request based on current mode and environment."""
        # Apply security layer if in secure mode and Embassai is available
        if self.mode == AgentMode.SECURE and self.embassai:
            if self.embassai_mode == EmbassaiMode.LOCAL:
                request = self.embassai.encrypt_request(request)
            elif self.embassai_mode == EmbassaiMode.REMOTE:
                # Send to remote Embassai server
                request = await self._send_to_embassai_server(request)
        
        # Process based on mode
        if self.mode == AgentMode.BROWSE:
            return await self._handle_browse(request)
        elif self.mode == AgentMode.BUILD:
            return await self._handle_build(request)
        elif self.mode == AgentMode.WRITE:
            return await self._handle_write(request)
        elif self.mode == AgentMode.EXECUTE:
            return await self._handle_execute(request)
        elif self.mode == AgentMode.REVIEW:
            return await self._handle_review(request)
        elif self.mode == AgentMode.SECURE:
            return await self._handle_secure(request)
        
        return {"error": "Invalid mode specified"}
    
    async def _send_to_embassai_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to remote Embassai server."""
        if not self.embassai or not isinstance(self.embassai, dict):
            return {"error": "Embassai not properly initialized"}
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.embassai['api_url']}/encrypt",
                json=request,
                headers={"X-API-Key": self.embassai["api_key"]}
            ) as response:
                return await response.json()
    
    def set_mode(self, mode: str):
        """Set the operational mode of the agent."""
        self.mode = mode
        self.agent.instructions = self._get_system_message()
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with the current mode and tools."""
        system_message = self._get_system_message()
        prompt = self._create_prompt(system_message)
        
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self._create_agent(prompt),
            tools=self.tools.tools,
            memory=self.memory,
            verbose=True
        )
    
    def _get_system_message(self) -> str:
        """Get the system message based on the current mode."""
        mode_messages = {
            "default": "You are a helpful AI assistant.",
            "task": "You are a task-oriented AI assistant focused on completing specific tasks efficiently.",
            "decision": "You are a decision-making AI assistant that helps analyze options and make informed choices.",
            "creative": "You are a creative AI assistant that helps generate innovative ideas and solutions."
        }
        return mode_messages.get(self.mode, mode_messages["default"])
    
    def _create_prompt(self, system_message: str):
        """Create the agent prompt with the system message."""
        return [
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    
    def _create_agent(self, prompt):
        """Create the agent with the given prompt."""
        return {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"]
        } | prompt | self.llm | OpenAIFunctionsAgentOutputParser()
    
    async def _handle_browse(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web browsing and data extraction tasks"""
        return {"status": "browsing", "request": request}
    
    async def _handle_build(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow building tasks"""
        return {"status": "building", "request": request}
    
    async def _handle_write(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content generation and research tasks"""
        return {"status": "writing", "request": request}
    
    async def _handle_execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow execution tasks"""
        return {"status": "executing", "request": request}
    
    async def _handle_review(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task review and optimization"""
        return {"status": "reviewing", "request": request}
    
    async def _handle_secure(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle secure mode tasks"""
        return {"status": "securing", "request": request}

    def _get_tools(self) -> list:
        """Get the list of tools from PraisonAI."""
        return [
            "WebSearchTool",
            "FileSystemTool",
            "APITool",
            "MemoryTool",
            "ProcessTool",
            "ReasoningTool",
            "WritingTool",
            "CodeTool",
            "DataTool",
            "MathTool",
            "TimeTool",
            "WeatherTool",
            "NewsTool",
            "TranslationTool",
            "SummarizationTool",
            "QuestionAnsweringTool",
            "ClassificationTool",
            "SentimentAnalysisTool",
            "EntityRecognitionTool",
            "KeywordExtractionTool",
            "TopicModelingTool",
            "TextGenerationTool",
            "TextCompletionTool",
            "TextEditingTool",
            "TextSummarizationTool",
            "TextClassificationTool",
            "TextSentimentTool",
            "TextEntityTool",
            "TextKeywordTool",
            "TextTopicTool"
        ] 