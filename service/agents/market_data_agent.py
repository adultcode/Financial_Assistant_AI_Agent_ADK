import os

from mcp import StdioServerParameters
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams, MCPToolset, StreamableHTTPConnectionParams
from google.genai import types
from mcp import StdioServerParameters

load_dotenv()  # Load environment variables from .env file

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


coinapi_toolset = McpToolset(
            connection_params=StdioConnectionParams(

                server_params=StdioServerParameters(command='npx',
                                                    args=[
                                                        'mcp-remote',
                                                        'https://mcp.api.coingecko.com/sse',
                                                        '--log-level',
                                                        'error',
                                                    ]),
                timeout=30,
            )
        )
# Create the agent responsible for market data
market_data_agent = LlmAgent(
    name="market_data_agent",
    output_key='market_data_result',
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""You are a market data agent. Your role is to provide real-time and historical
price information for financial assets, primarily cryptocurrencies, using the tools provided.

If user asks for suggestion list top rank,top gainer in 24h and other factors
When a user asks for the price of a cryptocurrency (e.g., 'what is the price of Bitcoin?'),
use the `MarketData` tool to fetch the latest information.
if need market news, future market prediction use this agent and tools
""",
    tools=[coinapi_toolset]
)

print("✅ Market Data Agent defined.")
