from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.sessions import InMemorySessionService
from google.genai import types

from service.agents.database_agent import database_agent
from service.db.database import init_db, get_all_transactions, add_transaction
import os
import asyncio
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, AgentTool


def first_app_run():
    print(" Hi, I am your financial assistant, what can I do for you? \n choose one of the commands:")
    print("💵 1) Add transaction")
    print("🎯 2) Set a goal")
    print("💲 3) Add investment")
    print("💲 4) get Transactions")
    user_command = int(input())

    match user_command:
        case 1:
            new_transaction()
        case 4:
            getAllTransactions()

def getAllTransactions():
    print(f"{get_all_transactions()}")
def Gettransaction_type(int:type):
    if(type==1):
        return "income"
    return "expense"
def new_transaction():
    print("----- ✅ Add transaction -----" )
    print("What is your transaction:")
    print("1: Income")
    print("2: Expense")
    transaction_type = int(input())
    if( transaction_type != 1 and transaction_type !=2):
        print("Invalid input")
        return
    amount = int(input("Enter amount: "))

    add_transaction(type=Gettransaction_type(transaction_type),amount=amount)



async def main():
    load_dotenv()  # Load environment variables from .env file
    init_db()
    #first_app_run()
    user_id = "my_user"

    try:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

        print(f"✅ Gemini API key setup complete. {GOOGLE_API_KEY}")

        retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
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
                        5- Financial advises
                        Your tool:
                        1: If user asks for adding anything to databse or getting list from saved data
                            use `database_agent` agent,
                        """,
            sub_agents=[database_agent],
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
                #print(f"Assistant: {response}")
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
