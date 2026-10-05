from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "expenses.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            amount REAL DEFAULT 0
        )
    """)
    conn.execute("INSERT OR IGNORE INTO budget (id, amount) VALUES (1, 0)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    transactions = conn.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()
    income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type = 'Income'"
    ).fetchone()[0]
    expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE transaction_type = 'Expense'"
    ).fetchone()[0]
    budget = conn.execute(
        "SELECT amount FROM budget WHERE id = 1"
    ).fetchone()[0]
    conn.close()

    return render_template(
        "index.html",
        transactions=transactions,
        income=income,
        expense=expense,
        balance=income - expense,
        budget=budget,
        remaining_budget=budget - expense
    )

@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        transaction_type = request.form["transaction_type"]
        category = request.form["category"]
        amount = float(request.form["amount"])
        description = request.form["description"]
        date = request.form["date"]

        conn = get_db()
        conn.execute("""
            INSERT INTO transactions
            (transaction_type, category, amount, description, date)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_type, category, amount, description, date))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add_transaction.html")

@app.route("/delete/<int:id>")
def delete_transaction(id):
    conn = get_db()
    conn.execute("DELETE FROM transactions WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/budget", methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        amount = float(request.form["amount"])
        conn = get_db()
        conn.execute("UPDATE budget SET amount = ? WHERE id = 1", (amount,))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    conn = get_db()
    budget = conn.execute("SELECT amount FROM budget WHERE id = 1").fetchone()[0]
    conn.close()
    return render_template("budget.html", budget=budget)

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
