import sqlite3
from datetime import datetime

DATABASE_NAME = 'my_database.db'

def get_db_connection():
    """Establishes a connection to the SQLite database and returns the connection object."""
    conn = sqlite3.connect(DATABASE_NAME)
    # Allows accessing columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create 'goal' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note TEXT NOT NULL,
                date_target TIMESTAMP NOT NULL,
                money_target INTEGER NOT NULL
            );
        ''')

        # Create 'transaction' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                amount REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Create 'invest' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        conn.commit()
        print("Database initialized and tables created successfully!")

# --- Goal Functions ---

def add_goal(note: str, date_target: datetime, money_target: int):
    """Adds a new goal to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO goal (note, date_target, money_target) VALUES (?, ?, ?)',
            (note, date_target, money_target)
        )
        conn.commit()

def get_all_goals():
    """Retrieves all goals from the database."""
    with get_db_connection() as conn:
        goals = conn.execute('SELECT * FROM goal').fetchall()
        return [dict(row) for row in goals]

# --- Transaction Functions ---

def add_transaction(type: str, amount: float):
    """Adds a new transaction (expense or income)."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO transaction_history (type, amount) VALUES (?, ?)',
            (type, amount)
        )
        conn.commit()

def get_all_transactions():
    """Retrieves all transactions from the database."""
    with get_db_connection() as conn:
        transactions = conn.execute('SELECT * FROM transaction_history ORDER BY created_at DESC').fetchall()
        print(f"transactions: {transactions}")
        return [dict(row) for row in transactions]

# --- Investment Functions ---

def add_investment(amount: float, title: str, price: float):
    """Adds a new investment to the database."""
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO invest (amount, title, price) VALUES (?, ?, ?)',
            (amount, title, price)
        )
        conn.commit()

def get_all_investments():
    """Retrieves all investments from the database."""
    with get_db_connection() as conn:
        investments = conn.execute('SELECT * FROM invest ORDER BY created_at DESC').fetchall()
        return [dict(row) for row in investments]


def get_transactions_by_type(transaction_type: str):
    """Retrieves all transactions of a specific type ('income' or 'expense')."""
    if transaction_type not in ('income', 'expense'):
        raise ValueError("Transaction type must be 'income' or 'expense'")
    with get_db_connection() as conn:
        transactions = conn.execute(
            'SELECT * FROM transaction_history WHERE type = ? ORDER BY created_at DESC',
            (transaction_type,)
        ).fetchall()
        return [dict(row) for row in transactions]


def get_transaction_totals_by_date_range(start_date: str, end_date: str):
    """Calculates the total income and expense within a given date range."""
    with get_db_connection() as conn:
        # The query sums up amounts for 'income' and 'expense' separately within the date range.
        # The date() function in SQLite ensures we compare only the date part of the timestamp.
        totals = conn.execute('''
                              SELECT type,
                                     SUM(amount) as total_amount
                              FROM transaction_history
                              WHERE
                                  date (created_at) BETWEEN ?
                                AND ?
                              GROUP BY
                                  type;
                              ''', (start_date, end_date)).fetchall()
        # The result is a list of rows, e.g., [('income', 5000), ('expense', 2500)].
        # We convert this into a more usable dictionary.
        return {row['type']: row['total_amount'] for row in totals}


# This block allows you to run `python database.py` to set up the DB for the first time.
if __name__ == '__main__':
    init_db()
