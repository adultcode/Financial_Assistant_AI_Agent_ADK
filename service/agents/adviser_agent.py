from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models import Gemini
from google.genai import types

from service.agents.database_agent import database_agent, GoalAndInvestment
from service.agents.market_data_agent import market_data_agent

load_dotenv()  # Load environment variables from .env file

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

profile_gathering_agent = LlmAgent(
    name="profile_gatherer",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    output_key="database_result",
    instruction="""You are a data gathering agent. Your only task is to get a complete overview of the user's financial data, including goals, investments, and transactions, by using the `GoalAndInvestment` tool.
    You must use the `GoalAndInvestment` tool. Do not ask the user for information.
    """,
    tools=[GoalAndInvestment]
)


final_adviser = LlmAgent(
    name="final_adviser",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    instruction="""You are an expert financial advisor.
    You have been provided with two pieces of information:
    1. The user's complete financial profile from the database, including their goals, current investments, and transaction history (available in the `database_result` context).
    2. The latest market data and predictions based on the user's query (available in the `market_data_result` context).

    Your task is to synthesize all this information to provide clear, actionable advice.
    - Analyze the user's goals (target amount and date).
    - Review their income/expense patterns from their transactions.
    - Consider their current investments.
    - Based on the market data and predictions, suggest specific investments or strategies to help them reach their goals within the remaining time.
    - Be direct and confident in your recommendations.
    """
)

adviser_agent = SequentialAgent(
    name="adviser_agent",
    description="""A financial adviser that first gathers user data and market data, then provides a recommendation.
    You investment advise is based on crypto market always,
    Never say i can not predict the future of market, use your market tool to get high gainer coins""",
    sub_agents=[
        profile_gathering_agent,
        market_data_agent,
        final_adviser],
)

print("✅ Adviser Agent (Sequential) created.")
