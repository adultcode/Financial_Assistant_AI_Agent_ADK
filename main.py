from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

from service.agents.database_agent import database_agent, GetTransactionsByType, GetAllTransactions, AddNewTransaction, \
    GetTransactionTotalsByDateRange, GetAllGoals, AddNewInvestment, GetAllInvestments, AddNewGoal, GoalAndInvestment
from service.agents.adviser_agent import adviser_agent
from service.db.database import init_db, get_all_transactions, add_transaction
import os
import asyncio
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner



async def main():
    load_dotenv()  # Load environment variables from .env file
    init_db()

    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

        print(f"✅ Gemini API key setup complete. {GOOGLE_API_KEY}")
        narket_data = McpToolset(
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
        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

        root_database_agent = LlmAgent(
            name="root_database_agent",
            model=Gemini(
                model="gemini-2.5-flash",
                retry_options=retry_config,
            ),
            output_key="database_result",
            instruction=database_agent.instruction,  # reuse same prompt
            tools=[
                AddNewTransaction,
                GetAllTransactions,
                GetTransactionsByType,
                GetTransactionTotalsByDateRange,
                AddNewGoal,
                GetAllGoals,
                AddNewInvestment,
                GetAllInvestments,
                GoalAndInvestment,
            ],
        )

        root_agent = Agent(
            name="Financial_Assistant",
            model=Gemini(
                model="gemini-2.5-flash",
                retry_options=retry_config
            ),
            description="A financial assistant help users to manage their finances.",
            instruction="""You are a helpful financial assistant. you are responsible to help user to make better investment to reach their goals.
                        Your crucial rules:
                        1- if user send greeting message say how can i help you?
                        2- if user ask out of topic question answer very short
                        3- Tell a short tip to user after every expense
                        4- suggest best investments to user based on current market data, goals and income amount
                        5- Answer Straight to the user investment questions and offer direct answer,
                        For example:
                            what is best investment for next year:
                                Correct answer: BTC or Gold
                                Wrong answer: I cannot offer advice. Predicting the future market is impossible and goes against my guidelines as a financial assistant.
                        You are high risk Financial assistant, tell the investment signal to the user based the market data,
                        do not limit your self
                        Your tools:
                        1. For simple database tasks (adding/retrieving data), use the `root_database_agent`.
                        2. For  market data lookups (like the current price of an asset,future prediction), use the `coinapi_toolset` .
                            Never say  cannot provide real-time market data
                        3. For complex questions that require financial advise, a plan to reach a goal, or suggestions , use the `adviser_agent`.
                        """,
            tools=[narket_data],
            sub_agents=[root_database_agent,  adviser_agent],
        ) # ✅ ONLY put actual tools here, not agents


        print("✅ Root Agent defined.")
        runner = InMemoryRunner(agent=root_agent)
        print("\n🤖 Your financial assistant is ready. Type 'exit' or 'quit' to end the chat.")
        print("-" * 60)
        # response = await runner.run_debug(
        #     "Hi"
        # )

        while True:
            try:
                prompt = input("You: ")
                if prompt.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                response = await  runner.run_debug(prompt)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting application.")
