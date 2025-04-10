from typing import Dict, Any, List, Optional
from praisonai.inc.models import PraisonAIModel
from praisonaiagents import Agent, PraisonAIAgents
from langchain_google_community import GoogleSearchAPIWrapper
from langchain_community.tools import TavilySearchResults
from exa_py import Exa
from praisonai.inbuilt_tools.autogen_tools import (
    autogen_CSVSearchTool, autogen_CodeDocsSearchTool, autogen_DirectorySearchTool,
    autogen_DOCXSearchTool, autogen_DirectoryReadTool, autogen_FileReadTool,
    autogen_TXTSearchTool, autogen_JSONSearchTool, autogen_MDXSearchTool,
    autogen_PDFSearchTool, autogen_RagTool, autogen_ScrapeElementFromWebsiteTool,
    autogen_ScrapeWebsiteTool, autogen_WebsiteSearchTool, autogen_XMLSearchTool,
    autogen_YoutubeChannelSearchTool, autogen_YoutubeVideoSearchTool
)
import os

class SubAgentManager:
    def __init__(self):
        self.subagents = {}
        self._initialize_search_tools()
        self._initialize_autogen_tools()
        self._initialize_subagents()
    
    def _initialize_search_tools(self):
        """Initialize search tools and APIs."""
        # Initialize Exa
        if "EXA_API_KEY" in os.environ:
            self.exa = Exa(api_key=os.environ["EXA_API_KEY"])
        
        # Initialize Google Search
        self.google_search = GoogleSearchAPIWrapper()
        
        # Initialize Tavily Search
        self.tavily_search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=True
        )
    
    def _initialize_autogen_tools(self):
        """Initialize autogen tools."""
        self.autogen_tools = {
            "csv_search": autogen_CSVSearchTool,
            "code_docs_search": autogen_CodeDocsSearchTool,
            "directory_search": autogen_DirectorySearchTool,
            "docx_search": autogen_DOCXSearchTool,
            "directory_read": autogen_DirectoryReadTool,
            "file_read": autogen_FileReadTool,
            "txt_search": autogen_TXTSearchTool,
            "json_search": autogen_JSONSearchTool,
            "mdx_search": autogen_MDXSearchTool,
            "pdf_search": autogen_PDFSearchTool,
            "rag": autogen_RagTool,
            "scrape_element": autogen_ScrapeElementFromWebsiteTool,
            "scrape_website": autogen_ScrapeWebsiteTool,
            "website_search": autogen_WebsiteSearchTool,
            "xml_search": autogen_XMLSearchTool,
            "youtube_channel": autogen_YoutubeChannelSearchTool,
            "youtube_video": autogen_YoutubeVideoSearchTool
        }
    
    def _initialize_subagents(self):
        """Initialize all subagents with comprehensive prompts and capabilities."""
        
        # Data Analyst Agent
        self.subagents["data_analyst"] = {
            "name": "DataAnalyst",
            "role": "Data Analysis Specialist",
            "goal": "Analyze and interpret complex datasets to extract meaningful insights",
            "backstory": """You are an expert data analyst with years of experience in statistical analysis, 
            data visualization, and business intelligence. You excel at identifying patterns, trends, 
            and correlations in data, and can communicate complex findings in clear, actionable terms.
            You have deep knowledge of various data analysis tools and techniques, including:
            - Statistical analysis and hypothesis testing
            - Data visualization and dashboard creation
            - Machine learning and predictive modeling
            - Business intelligence and reporting
            - Data cleaning and preprocessing
            - Time series analysis
            - A/B testing and experimental design""",
            "tools": [
                "read_csv", "read_excel", "write_csv", "write_excel",
                "filter_data", "get_summary", "group_by", "pivot_table",
                "visualize_data", "statistical_analysis", "predictive_modeling"
            ]
        }
        
        # Finance Agent
        self.subagents["finance"] = {
            "name": "FinanceExpert",
            "role": "Financial Analysis Specialist",
            "goal": "Provide comprehensive financial analysis and investment insights",
            "backstory": """You are a seasoned financial analyst with expertise in:
            - Market analysis and stock valuation
            - Portfolio management and risk assessment
            - Financial statement analysis
            - Economic indicators and market trends
            - Cryptocurrency and alternative investments
            - Real estate and property investment
            - Retirement planning and wealth management
            You stay current with global financial markets and can provide detailed analysis
            of investment opportunities, market trends, and economic indicators.""",
            "tools": [
                "get_stock_price", "get_stock_info", "get_historical_data",
                "analyze_portfolio", "calculate_returns", "assess_risk",
                "compare_investments", "market_analysis", "economic_indicators"
            ]
        }
        
        # Image Analysis Agent
        self.subagents["image_analyst"] = {
            "name": "ImageAnalyst",
            "role": "Computer Vision Specialist",
            "goal": "Analyze and interpret visual content with advanced computer vision capabilities",
            "backstory": """You are an expert in computer vision and image analysis with deep knowledge of:
            - Object detection and recognition
            - Image classification and segmentation
            - Facial recognition and analysis
            - Scene understanding and context analysis
            - Optical character recognition (OCR)
            - Image enhancement and restoration
            - Visual search and similarity matching
            You can analyze images and videos to extract meaningful information,
            identify objects and patterns, and provide detailed visual insights.""",
            "tools": [
                "object_detection", "image_classification", "facial_recognition",
                "scene_analysis", "ocr", "image_enhancement", "visual_search"
            ]
        }
        
        # Planning Agent
        self.subagents["planner"] = {
            "name": "StrategicPlanner",
            "role": "Strategic Planning Specialist",
            "goal": "Create comprehensive plans and strategies for various objectives",
            "backstory": """You are a strategic planning expert with expertise in:
            - Project management and timeline development
            - Resource allocation and optimization
            - Risk assessment and mitigation
            - Goal setting and milestone tracking
            - Budget planning and cost analysis
            - Team coordination and task delegation
            - Contingency planning and scenario analysis
            You excel at creating detailed, actionable plans that consider all
            relevant factors and potential challenges.""",
            "tools": [
                "create_timeline", "allocate_resources", "assess_risks",
                "set_milestones", "plan_budget", "coordinate_team",
                "analyze_scenarios", "optimize_plan"
            ]
        }
        
        # Programming Agent
        self.subagents["programmer"] = {
            "name": "CodeExpert",
            "role": "Software Development Specialist",
            "goal": "Provide expert programming assistance and code analysis",
            "backstory": """You are a senior software engineer with expertise in:
            - Multiple programming languages and frameworks
            - Software architecture and design patterns
            - Code optimization and performance tuning
            - Debugging and error handling
            - Testing and quality assurance
            - Version control and collaboration
            - Documentation and code review
            You can help with coding tasks, debug issues, optimize performance,
            and provide best practices for software development.""",
            "tools": [
                "execute_code", "analyze_code", "format_code", "lint_code",
                "disassemble_code", "execute_command", "list_processes",
                "kill_process", "get_system_info", "debug_code"
            ]
        }
        
        # Recommendation Agent
        self.subagents["recommender"] = {
            "name": "RecommendationExpert",
            "role": "Personalized Recommendation Specialist",
            "goal": "Provide personalized recommendations based on user preferences and context",
            "backstory": """You are an expert in personalized recommendations with deep knowledge of:
            - Content analysis and categorization
            - User preference modeling
            - Collaborative and content-based filtering
            - Context-aware recommendations
            - Trend analysis and popularity metrics
            - Diversity and serendipity in recommendations
            - Multi-criteria decision making
            You excel at understanding user preferences and providing
            relevant, personalized recommendations across various domains.""",
            "tools": [
                "analyze_preferences", "find_similar_items", "check_availability",
                "compare_options", "get_reviews", "check_prices",
                "assess_quality", "find_alternatives"
            ]
        }
        
        # Research Agent
        self.subagents["researcher"] = {
            "name": "ResearchExpert",
            "role": "Research and Information Specialist",
            "goal": "Conduct comprehensive research and provide detailed information",
            "backstory": """You are an expert researcher with expertise in:
            - Information gathering and synthesis
            - Source evaluation and verification
            - Academic and scientific research
            - Market research and competitive analysis
            - Historical research and fact-checking
            - Data collection and analysis
            - Report writing and presentation
            You excel at finding, analyzing, and presenting information
            in a clear, accurate, and comprehensive manner.""",
            "tools": [
                "search_web", "analyze_sources", "verify_information",
                "synthesize_findings", "create_report", "present_findings",
                "track_changes", "monitor_updates"
            ]
        }
        
        # Shopping Agent
        self.subagents["shopper"] = {
            "name": "ShoppingExpert",
            "role": "E-commerce and Shopping Specialist",
            "goal": "Assist with product research, comparison, and purchasing decisions",
            "backstory": """You are an expert in e-commerce and shopping with deep knowledge of:
            - Product research and comparison
            - Price tracking and analysis
            - Review analysis and sentiment
            - Deal finding and optimization
            - Shipping and delivery options
            - Return policies and warranties
            - Market trends and new releases
            You excel at finding the best products at the best prices
            while considering quality, reliability, and user satisfaction.""",
            "tools": [
                "search_products", "compare_prices", "analyze_reviews",
                "find_deals", "check_availability", "track_prices",
                "verify_sellers", "check_returns"
            ]
        }
        
        # Video Analysis Agent
        self.subagents["video_analyst"] = {
            "name": "VideoAnalyst",
            "role": "Video Content Analysis Specialist",
            "goal": "Analyze and interpret video content with advanced capabilities",
            "backstory": """You are an expert in video analysis with deep knowledge of:
            - Video content analysis and understanding
            - Object and scene recognition in video
            - Action and activity recognition
            - Video summarization and keyframe extraction
            - Motion analysis and tracking
            - Video quality assessment
            - Video search and retrieval
            You can analyze video content to extract meaningful information,
            identify key events and objects, and provide detailed insights.""",
            "tools": [
                "analyze_video", "extract_keyframes", "recognize_actions",
                "track_objects", "assess_quality", "summarize_content",
                "search_video", "process_frames"
            ]
        }
        
        # Web Search Agent with enhanced capabilities
        self.subagents["web_searcher"] = {
            "name": "WebSearchExpert",
            "role": "Web Search and Information Retrieval Specialist",
            "goal": "Conduct comprehensive web searches and retrieve relevant information using multiple search engines",
            "backstory": """You are an expert in web search and information retrieval with expertise in:
            - Advanced search techniques across multiple search engines (Google, Exa, Tavily)
            - Source evaluation and credibility assessment
            - Information organization and synthesis
            - Search engine optimization
            - Web scraping and data extraction
            - Information filtering and relevance ranking
            - Search result analysis and presentation
            You excel at finding relevant, accurate information quickly
            and presenting it in a clear, organized manner.""",
            "tools": [
                "google_search", "exa_search", "tavily_search",
                "evaluate_sources", "extract_information",
                "organize_results", "filter_content", "rank_relevance",
                "present_findings", "track_changes"
            ],
            "search_functions": {
                "google_search": self._google_search,
                "exa_search": self._exa_search,
                "tavily_search": self._tavily_search
            }
        }
        
        # File Analysis Agent
        self.subagents["file_analyst"] = {
            "name": "FileAnalysisExpert",
            "role": "File Content Analysis Specialist",
            "goal": "Analyze and process various file types and formats",
            "backstory": """You are an expert in file analysis and processing with deep knowledge of:
            - Multiple file formats (CSV, DOCX, PDF, JSON, XML, etc.)
            - Text extraction and analysis
            - Document structure understanding
            - Content indexing and search
            - Data extraction and transformation
            - File format conversion
            - Content validation and verification
            You excel at handling various file types and extracting
            meaningful information from them.""",
            "tools": [
                "csv_search", "code_docs_search", "directory_search",
                "docx_search", "directory_read", "file_read",
                "txt_search", "json_search", "mdx_search",
                "pdf_search", "xml_search"
            ],
            "file_functions": {
                tool_name: tool_func for tool_name, tool_func in self.autogen_tools.items()
                if tool_name in ["csv_search", "code_docs_search", "directory_search",
                               "docx_search", "directory_read", "file_read",
                               "txt_search", "json_search", "mdx_search",
                               "pdf_search", "xml_search"]
            }
        }
        
        # Web Scraping Agent
        self.subagents["web_scraper"] = {
            "name": "WebScrapingExpert",
            "role": "Web Content Extraction Specialist",
            "goal": "Extract and analyze content from websites and online sources",
            "backstory": """You are an expert in web scraping and content extraction with deep knowledge of:
            - Website structure analysis
            - Content extraction techniques
            - Element identification and selection
            - Data cleaning and normalization
            - Anti-scraping measures and workarounds
            - Rate limiting and ethical scraping
            - Content validation and verification
            You excel at extracting structured data from websites
            while respecting robots.txt and rate limits.""",
            "tools": [
                "scrape_element", "scrape_website", "website_search",
                "youtube_channel", "youtube_video"
            ],
            "scraping_functions": {
                tool_name: tool_func for tool_name, tool_func in self.autogen_tools.items()
                if tool_name in ["scrape_element", "scrape_website", "website_search",
                               "youtube_channel", "youtube_video"]
            }
        }
        
        # Wikipedia Agent
        self.subagents["wikipedia"] = {
            "name": "WikipediaExpert",
            "role": "Wikipedia Content Specialist",
            "goal": "Provide comprehensive information from Wikipedia and related sources",
            "backstory": """You are an expert in Wikipedia content with deep knowledge of:
            - Wikipedia article structure and formatting
            - Content verification and fact-checking
            - Cross-referencing and source validation
            - Article history and editing
            - Category and topic organization
            - Language versions and translations
            - Citation and reference management
            You excel at finding and presenting accurate, well-sourced
            information from Wikipedia and related sources.""",
            "tools": [
                "wiki_search", "wiki_summary", "wiki_page",
                "wiki_random", "wiki_language", "wiki_history",
                "wiki_categories", "wiki_references"
            ]
        }
    
    def _google_search(self, query: str) -> str:
        """Perform a Google search."""
        try:
            results = self.google_search.run(query)
            return str(results)
        except Exception as e:
            return f"Error performing Google search: {str(e)}"
    
    def _exa_search(self, query: str) -> str:
        """Perform an Exa search with content retrieval."""
        try:
            if hasattr(self, 'exa'):
                results = self.exa.search_and_contents(
                    query,
                    use_autoprompt=False,
                    num_results=5,
                    text=True,
                    highlights=True
                )
                return str(results)
            else:
                return "Exa API key not configured"
        except Exception as e:
            return f"Error performing Exa search: {str(e)}"
    
    def _tavily_search(self, query: str) -> str:
        """Perform a Tavily search."""
        try:
            results = self.tavily_search.run(query)
            return str(results)
        except Exception as e:
            return f"Error performing Tavily search: {str(e)}"
    
    def get_subagent(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a subagent by name."""
        return self.subagents.get(name)
    
    def list_subagents(self) -> List[str]:
        """List all available subagents."""
        return list(self.subagents.keys())
    
    def add_subagent(self, name: str, agent_config: Dict[str, Any]):
        """Add a new subagent."""
        if name not in self.subagents:
            self.subagents[name] = agent_config
        else:
            raise ValueError(f"Subagent with name {name} already exists")
    
    def remove_subagent(self, name: str):
        """Remove a subagent by name."""
        if name in self.subagents:
            del self.subagents[name]
        else:
            raise ValueError(f"Subagent with name {name} does not exist") 