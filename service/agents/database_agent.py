from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from service.db.database import add_transaction, get_all_transactions, add_goal, get_all_goals, add_investment, \
    get_all_investments

retry_config = types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1,
            http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
        )

def AddNewTransaction(transaction_type:str,transaction_amount:float)->dict:
    """
    Adds a new transaction (income or expense) to the database.
    Use this when a user wants to record a new income or expense.
    Args:
        transaction_type: The type of transaction. Must be either 'income' or 'expense'.
        transaction_amount: The amount of the transaction as a float.
    Returns:
        A dictionary with a status and a message.
    """

    try:
        add_transaction(type = transaction_type,amount = transaction_amount)
        return {"status": "success", "message": "Your transaction saved successfully"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def GetAllTransactions() -> dict:
    """
    Retrieves all transactions (both income and expense) from the database.
    Use this when a user asks to see their transaction history or a list of their transactions.
    Returns:
        A dictionary containing the list of transactions or an error message.
    """
    try:
        transactions = get_all_transactions()
        return {"status": "success", "data": transactions}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def AddNewGoal(note: str, date_target: str, money_target: int) -> dict:
    """
    Adds a new financial goal to the database.
    Use this when a user wants to set a new goal.
    Args:
        note: A description of the goal.
        date_target: The target date for the goal in 'YYYY-MM-DD' format.
        money_target: The target amount of money for the goal.
    Returns:
        A dictionary with a status and a message.
    """
    try:
        target_date = datetime.strptime(date_target, '%Y-%m-%d')
        add_goal(note=note, date_target=target_date, money_target=money_target)
        return {"status": "success", "message": "Your goal was saved successfully."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def GetAllGoals() -> dict:
    """
    Retrieves all financial goals from the database.
    Use this when a user asks to see their list of goals.
    Returns:
        A dictionary containing the list of goals or an error message.
    """
    try:
        goals = get_all_goals()
        return {"status": "success", "data": goals}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def AddNewInvestment(amount: float, title: str, price: float) -> dict:
    """
    Adds a new investment record to the database.
    Use this when a user wants to record a new investment they made.
    Args:
        amount: The quantity or amount of the asset invested.
        title: The name or symbol of the investment (e.g., 'Bitcoin', 'AAPL').
        price: The price at which the investment was made.
    Returns:
        A dictionary with a status and a message.
    """
    try:
        add_investment(amount=amount, title=title, price=price)
        return {"status": "success", "message": "Your investment was saved successfully."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def GetAllInvestments() -> dict:
    """
    Retrieves all investment records from the database.
    Use this when a user asks to see their list of investments.
    Returns:
        A dictionary containing the list of investments or an error message.
    """
    try:
        investments = get_all_investments()
        return {"status": "success", "data": investments}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}


database_agent = LlmAgent(
    name="database_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),

    instruction="""You are a database agent responsible for managing user's financial data.
You can add and retrieve records from the database.

Use the following tools based on the user's request:
- To add a new transaction (income or expense), use the `AddNewTransaction` tool.
- To get a list of all transactions, use the `GetAllTransactions` tool.
- To add a new financial goal, use the `AddNewGoal` tool.
- To get a list of all goals, use the `GetAllGoals` tool.
- To add a new investment, use the `AddNewInvestment` tool.
- To get a list of all investments, use the `GetAllInvestments` tool.
""",
    output_key="blog_outline",
    tools=[AddNewTransaction, GetAllTransactions, AddNewGoal, GetAllGoals, AddNewInvestment, GetAllInvestments]
)
print("✅ Database Agent defined.")