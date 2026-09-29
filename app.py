from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = "barberbook.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT NOT NULL,
            barber TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "").strip()
        barber = request.form.get("barber", "").strip()
        date = request.form.get("date", "").strip()
        time = request.form.get("time", "").strip()

        if not all([name, email, service, barber, date, time]):
            return render_template(
                "booking.html",
                error="Please complete all fields."
            ), 400

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO appointments
            (name, email, service, barber, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, email, service, barber, date, time)
        )

        conn.commit()
        conn.close()

        return render_template(
            "confirmation.html",
            name=name,
            service=service,
            barber=barber,
            date=date,
            time=time
        )

    return render_template("booking.html")


@app.route("/admin")
def admin():
    conn = get_db_connection()

    appointments = conn.execute(
        """
        SELECT *
        FROM appointments
        ORDER BY date, time
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        appointments=appointments
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
