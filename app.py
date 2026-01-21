import datetime
from flask import Flask, render_template, request, redirect, url_for
from db import get_db


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


# ---------------- VIEW EXPENSES ----------------
@app.route("/view_expense")
def view_expense():
    conn = get_db()
    expenses = conn.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()
    conn.close()

    total = sum(e["amount"] for e in expenses)

    category = {}
    for e in expenses:
        category[e["category"]] = category.get(e["category"], 0) + e["amount"]

    return render_template(
        "view_expense.html",
        expense=expenses,
        total=total,
        category=category
    )


# ---------------- ADD EXPENSE ----------------
@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            """
            INSERT INTO expenses (category, amount, notes, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                request.form["category"].title(),
                float(request.form["amount"]),
                request.form["notes"].capitalize(),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("view_expense"))

    return render_template("add_expense.html")


# ---------------- EDIT EXPENSE (GET) ----------------
@app.route("/edit_expense/<int:id>")
def edit_expense(id):
    conn = get_db()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (id,)
    ).fetchone()
    conn.close()

    if not expense:
        return redirect(url_for("view_expense"))

    return render_template("edit.html", expense=expense)


# ---------------- UPDATE EXPENSE (POST) ----------------
@app.route("/update/<int:id>", methods=["POST"])
def update_expense(id):
    conn = get_db()
    conn.execute(
        """
        UPDATE expenses
        SET category = ?, amount = ?, notes = ?
        WHERE id = ?
        """,
        (
            request.form["category"].title(),
            float(request.form["amount"]),
            request.form["notes"].capitalize(),
            id
        )
    )
    conn.commit()
    conn.close()
    return redirect(url_for("view_expense"))


# ---------------- DELETE EXPENSE ----------------
@app.route("/delete_expense/<int:id>")
def delete_expense(id):
    conn = get_db()
    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("view_expense"))


if __name__ == "__main__":
    app.run(debug=True)
