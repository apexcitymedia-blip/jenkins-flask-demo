
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, render_template_string
)
import os
import sqlite3
import secrets
import hmac
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from flask_mail import Mail, Message

import smtplib
import threading
from email.message import EmailMessage

import json
import urllib.request
import urllib.error

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE = os.environ.get("DATABASE_PATH", "barberbook.db")
print("BarberBook database file:", os.path.abspath(DATABASE) if not DATABASE_URL else "PostgreSQL")
app.secret_key = os.environ.get("SECRET_KEY")
app.config.update(
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.environ.get("MAIL_PORT", "587")),
    MAIL_USE_TLS=os.environ.get("MAIL_USE_TLS", "True").lower() == "true",
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.environ.get("MAIL_USERNAME"),
)

app.config["MAIL_TIMEOUT"] = 2
mail = Mail(app)
def send_booking_confirmation(name, email, service, barber, date_text, time_text):
    try:
        message = Message(
            subject="Your BarberBook Appointment Confirmation",
            recipients=[email],
            body=(
                f"Hello {name},\n\n"
                "Your BarberBook appointment is confirmed!\n\n"
                f"Service: {service}\n"
                f"Barber: {barber}\n"
                f"Date: {date_text}\n"
                f"Time: {time_text}\n\n"
                "We look forward to seeing you!\n\n"
                "The BarberBook Team"
            ),
        )
        mail.send(message)
        app.logger.info("Booking confirmation email sent.")
    except Exception:
        app.logger.exception(
            "Booking was saved, but confirmation email sending failed."
        )

def send_appointment_decision(
    name, email, service, barber, date_text, time_text, status
):
    status = status.strip().lower()

    if status not in ("accepted", "rejected"):
        app.logger.warning("Unknown appointment status: %s", status)
        return

    if status == "accepted":
        subject = "Your BarberBook appointment is confirmed"
        decision = "accepted"
    else:
        subject = "Update on your BarberBook appointment"
        decision = "rejected"

    body = (
        f"Hi {name},\n\n"
        f"Your appointment request has been {decision}.\n\n"
        f"Service: {service}\n"
        f"Barber: {barber}\n"
        f"Date: {date_text}\n"
        f"Time: {time_text}\n\n"
        "Thank you for choosing BarberBook."
    )

    send_email_with_timeout(subject, email, body)

def send_email_with_timeout(subject, email, body):
    api_key = os.environ.get("RESEND_API_KEY")

    if not api_key:
        app.logger.error("RESEND_API_KEY is not configured.")
        return

    sender = os.environ.get(
        "RESEND_FROM_EMAIL",
        "onboarding@resend.dev",
    )

    payload = {
        "from": sender,
        "to": [email],
        "subject": subject,
        "text": body,
    }

    request = urllib.request.Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "BarberBook/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            app.logger.info(
                "Resend API response: %s",
                response.status,
            )
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        app.logger.error(
            "Resend rejected email: HTTP %s — %s",
            error.code,
            details,
        )
    except Exception:
        app.logger.exception("Resend email delivery failed.")


# ==========================================
# BARBERBOOK APPOINTMENT SETTINGS
# ==========================================

SHOP_TIMEZONE = ZoneInfo("Europe/Rome")

OPENING_TIME = time(7, 0)
CLOSING_TIME = time(23, 0)
SERVICE_DURATIONS = {
    "Haircut": 30,
    "Beard Trim": 15,
    "Hair + Beard": 45,
}

SERVICE_PRICES = {
    "Haircut": 10,
    "Beard Trim": 5,
    "Hair + Beard": 15,
}

ALLOWED_BARBERS = {"Alex", "Mike", "James"}

if DATABASE_URL:
    import psycopg
    from psycopg.rows import dict_row


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    if DATABASE_URL:
        return psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row
        )

    conn = sqlite3.connect(
        DATABASE,
        timeout=15
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    try:
        if DATABASE_URL:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS appointments (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    service TEXT NOT NULL,
                    barber TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                ALTER TABLE appointments
                ADD COLUMN IF NOT EXISTS status
                TEXT NOT NULL DEFAULT 'Pending'
                """
            )

            conn.execute(
                """
                ALTER TABLE appointments
                ADD COLUMN IF NOT EXISTS paid_at TEXT
                """
            )
            conn.execute(
                """
                ALTER TABLE appointments
                ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10, 2)
                """
            )

            conn.execute(
                """
                ALTER TABLE appointments
                ADD COLUMN IF NOT EXISTS phone TEXT
                """
            )

        else:
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

            columns = conn.execute(
                "PRAGMA table_info(appointments)"
            ).fetchall()

            if not any(column["name"] == "status" for column in columns):
                conn.execute(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'
                    """
                )

            if not any(column["name"] == "paid_at" for column in columns):
                conn.execute(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN paid_at TEXT
                    """
                )

            if not any(column["name"] == "paid_amount" for column in columns):
                conn.execute(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN paid_amount NUMERIC(10, 2)
                    """
                )

            if not any(column["name"] == "phone" for column in columns):
                conn.execute(
                    """
                    ALTER TABLE appointments
                    ADD COLUMN phone TEXT
                    """
                )

        conn.commit()

    finally:
        conn.close()


init_db()


# ==========================================
# ADMIN AUTHENTICATION
# ==========================================

def admin_configured():
    return all([
        app.secret_key,
        os.environ.get("ADMIN_USERNAME"),
        os.environ.get("ADMIN_PASSWORD"),
    ])


LOGIN_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BarberBook Admin Login</title>
</head>
<body style="font-family:Arial,sans-serif;max-width:380px;margin:60px auto;padding:20px">
  <h1>Admin Login</h1>
  {% if error %}
    <p style="color:#b00020">{{ error }}</p>
  {% endif %}
  <form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <p>
      <label for="username">Username</label><br>
      <input id="username" name="username" required autocomplete="username">
    </p>
    <p>
      <label for="password">Password</label><br>
      <input id="password" name="password" type="password" required autocomplete="current-password">
    </p>
    <button type="submit">Log in</button>
  </form>
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if not admin_configured():
        return "Admin login is not configured.", 503

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        saved_token = session.get("login_csrf_token", "")

        if not saved_token or not hmac.compare_digest(
            submitted_token, saved_token
        ):
            return (
                "Invalid form token. Please reload the login page.",
                400
            )

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        valid_username = hmac.compare_digest(
            username, os.environ["ADMIN_USERNAME"]
        )
        valid_password = hmac.compare_digest(
            password, os.environ["ADMIN_PASSWORD"]
        )

        session.pop("login_csrf_token", None)

        if valid_username and valid_password:
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))

        new_token = secrets.token_urlsafe(32)
        session["login_csrf_token"] = new_token

        return render_template_string(
            LOGIN_PAGE,
            error="Incorrect username or password.",
            csrf_token=new_token,
        ), 401

    token = secrets.token_urlsafe(32)
    session["login_csrf_token"] = token

    return render_template_string(
        LOGIN_PAGE,
        error=None,
        csrf_token=token,
    )


# ==========================================
# HOMEPAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# SMART APPOINTMENT BOOKING
# ==========================================

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "GET":
        return render_template("booking.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    service = request.form.get("service", "").strip()
    barber = request.form.get("barber", "").strip()
    date_text = request.form.get("date", "").strip()
    time_text = request.form.get("time", "").strip()

    def booking_error(message):
        return render_template(
            "booking.html",
            error=message
        ), 400

    # Validate required fields.
    if not all([
        name, email, service, barber, date_text, time_text
    ]):
        return booking_error("Please complete all fields.")

    # Validate basic input lengths and email format.
    if (
        len(name) > 100
        or len(email) > 254
        or "@" not in email
        or email.startswith("@")
        or email.endswith("@")
    ):
        return booking_error(
            "Please enter a valid name and email address."
        )

    # Accept only known services and barbers.
    if service not in SERVICE_DURATIONS:
        return booking_error("Please select a valid service.")

    if barber not in ALLOWED_BARBERS:
        return booking_error("Please select a valid barber.")

    # Parse the submitted date and time strictly.
    try:
        appointment_date = date.fromisoformat(date_text)
        parsed_time = datetime.strptime(
            time_text, "%H:%M"
        ).time()

        # Ensure the date is in the expected YYYY-MM-DD format.
        if appointment_date.isoformat() != date_text:
            raise ValueError("Invalid date format")

    except ValueError:
        return booking_error(
            "Please enter a valid appointment date and time."
        )

    now = datetime.now(SHOP_TIMEZONE)

    start = datetime.combine(
        appointment_date,
        parsed_time,
        tzinfo=SHOP_TIMEZONE
    )

    duration = SERVICE_DURATIONS[service]
    end = start + timedelta(minutes=duration)

    # Reject past appointments.
    if start < now:
        return booking_error(
            "Please choose a future appointment time."
        )

    # The entire service must fit within opening hours.
    if (
        parsed_time < OPENING_TIME
        or end.date() != appointment_date
        or end.time().replace(tzinfo=None) > CLOSING_TIME
    ):
        return booking_error(
            "Your appointment must start at or after 07:00 "
            "and finish by 23:00."
        )

    conn = None

    try:
        conn = get_db_connection()
        placeholder = "%s" if DATABASE_URL else "?"

        if DATABASE_URL:
            conn.execute(
                """
                SELECT pg_advisory_xact_lock(
                    hashtextextended(%s, 0)
                )
                """,
                (barber,)
            )
        else:
            conn.execute("BEGIN IMMEDIATE")

        existing_appointments = conn.execute(
            f"""
            SELECT service, time
            FROM appointments
            WHERE barber = {placeholder}
              AND date = {placeholder}
            """,
            (barber, date_text)
        ).fetchall()

        for existing in existing_appointments:
            existing_time_text = str(existing["time"])

            try:
                existing_start_time = datetime.strptime(
                    existing_time_text, "%H:%M"
                ).time()
            except ValueError:
                existing_start_time = datetime.strptime(
                    existing_time_text, "%H:%M:%S"
                ).time()

            existing_start = datetime.combine(
                appointment_date,
                existing_start_time,
                tzinfo=SHOP_TIMEZONE
            )

            existing_duration = SERVICE_DURATIONS.get(
                existing["service"], 60
            )
            existing_end = existing_start + timedelta(
                minutes=existing_duration
            )

            if start < existing_end and existing_start < end:
                conn.rollback()
                return booking_error(
                    "That time is unavailable for this barber. "
                    "Please choose another time."
                )

        conn.execute(
            f"""
            INSERT INTO appointments
                (name, email, phone, service, barber, date, time)
            VALUES
                ({placeholder}, {placeholder}, {placeholder},
                 {placeholder}, {placeholder}, {placeholder},
                 {placeholder})
            """,
            (
                name,
                email,
                phone,
                service,
                barber,
                date_text,
                time_text
            )
        )

        conn.commit()

    except Exception:
        if conn is not None:
            conn.rollback()
        app.logger.exception("Appointment booking failed.")
        return booking_error(
            "We couldn't complete your booking. Please try again."
        )
    finally:
        if conn is not None:
            conn.close()

    # Email sending is temporarily disabled while Render's SMTP connection is investigated.

    return render_template(
        "confirmation.html",
        name=name,
        service=service,
        barber=barber,
        date=date_text,
        time=time_text
    )
# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():
    if not admin_configured():
        return "Admin login is not configured.", 503

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    try:
        appointments = conn.execute(
            """
            SELECT *
            FROM appointments
            ORDER BY date, time
            """
        ).fetchall()
    finally:
        conn.close()

    total_appointments = len(appointments)
    pending_appointments = sum(
        1 for appointment in appointments
        if appointment["status"] == "Pending"
    )
    accepted_appointments = sum(
        1 for appointment in appointments
        if appointment["status"] == "Accepted"
    )
    rejected_appointments = sum(
        1 for appointment in appointments
        if appointment["status"] == "Rejected"
    )
    paid_appointments = sum(
        1 for appointment in appointments
        if appointment["status"] == "Paid"
    )
    def recorded_amount(appointment):
        saved_amount = appointment["paid_amount"]

        if saved_amount is not None:
            return float(saved_amount)

        # Fallback for older payments without a saved amount
        return float(SERVICE_PRICES.get(appointment["service"], 0))

    total_revenue = sum(
        recorded_amount(appointment)
        for appointment in appointments
        if appointment["status"] == "Paid"
    )

    unpaid_accepted_value = sum(
        SERVICE_PRICES.get(appointment["service"], 0)
        for appointment in appointments
        if appointment["status"] == "Accepted"
    )

    revenue_by_service = {
        service: sum(
            recorded_amount(appointment)
            for appointment in appointments
            if appointment["status"] == "Paid"
            and appointment["service"] == service
        )
        for service in SERVICE_PRICES
    }
    # Monthly revenue based on actual payment date
    monthly_revenue = {}
    monthly_paid_counts = {}
    monthly_service_revenue = {}

    for appointment in appointments:
        if appointment["status"] == "Paid" and appointment["paid_at"]:
            month_key = str(appointment["paid_at"])[:7]
            service = appointment["service"]
            price = recorded_amount(appointment)

            monthly_revenue[month_key] = (
                monthly_revenue.get(month_key, 0) + price
            )

            monthly_paid_counts[month_key] = (
                monthly_paid_counts.get(month_key, 0) + 1
            )

            if month_key not in monthly_service_revenue:
                monthly_service_revenue[month_key] = {}

            monthly_service_revenue[month_key][service] = (
                monthly_service_revenue[month_key].get(service, 0) + price
            )

    current_month = datetime.now(SHOP_TIMEZONE).strftime("%Y-%m")
    selected_month = request.args.get("month", current_month)

    if (
        len(selected_month) != 7
        or selected_month[4] != "-"
        or not selected_month[:4].isdigit()
        or not selected_month[5:].isdigit()
        or not 1 <= int(selected_month[5:]) <= 12
    ):
        selected_month = current_month

    year, month = map(int, selected_month.split("-"))
    previous_month = (
        f"{year - 1}-12" if month == 1
        else f"{year}-{month - 1:02d}"
    )

    selected_month_revenue = monthly_revenue.get(selected_month, 0)
    selected_month_payments = monthly_paid_counts.get(selected_month, 0)
    previous_month_revenue = monthly_revenue.get(previous_month, 0)
    selected_month_services = monthly_service_revenue.get(
        selected_month, {}
    )
    filtered_appointments = [
    appointment for appointment in appointments
    if appointment["paid_at"]
    and str(appointment["paid_at"])[:7] == selected_month
]

    token = secrets.token_urlsafe(32)
    session["admin_csrf_token"] = token

    return render_template(
        "admin.html",
appointments=appointments,
        csrf_token=token,
        total_appointments=total_appointments,
        pending_appointments=pending_appointments,
        accepted_appointments=accepted_appointments,
                rejected_appointments=rejected_appointments,
        paid_appointments=paid_appointments,
        total_revenue=total_revenue,
        unpaid_accepted_value=unpaid_accepted_value,
revenue_by_service=revenue_by_service,
monthly_revenue=monthly_revenue,
selected_month=selected_month,
selected_month_revenue=selected_month_revenue,
selected_month_payments=selected_month_payments,
previous_month_revenue=previous_month_revenue,
selected_month_services=selected_month_services
    )

@app.route(
    "/admin/appointment/<int:appointment_id>/status",
    methods=["POST"]
)
def update_appointment_status(appointment_id):
    if not admin_configured():
        return "Admin login is not configured.", 503

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("admin_csrf_token", "")

    if (
        not saved_token
        or not hmac.compare_digest(submitted_token, saved_token)
    ):
        return "Invalid form token. Please reload the dashboard.", 400

    new_status = request.form.get("status", "")

    if new_status not in {"Accepted", "Rejected"}:
        return "Invalid appointment status.", 400

    conn = get_db_connection()
    appointment = None

    try:
        placeholder = "%s" if DATABASE_URL else "?"

        appointment = conn.execute(
            f"""
            SELECT name, email, service, barber, date, time
            FROM appointments
            WHERE id = {placeholder}
              AND status = 'Pending'
            """,
            (appointment_id,)
        ).fetchone()

        if appointment is None:
            return (
                "Appointment not found or already processed. "
                "Please reload the dashboard.",
                409
            )

        result = conn.execute(
            f"""
            UPDATE appointments
            SET status = {placeholder}
            WHERE id = {placeholder}
              AND status = 'Pending'
            """,
            (new_status, appointment_id)
        )

        if result.rowcount == 0:
            conn.rollback()
            return (
                "Appointment has already been processed. "
                "Please reload the dashboard.",
                409
            )

        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Appointment status update failed.")
        return "Could not update the appointment. Please try again.", 500

    finally:
        conn.close()



    try:
        threading.Thread(
            target=send_appointment_decision,
            kwargs={
                "name": appointment["name"],
                "email": appointment["email"],
                "service": appointment["service"],
                "barber": appointment["barber"],
                "date_text": str(appointment["date"]),
                "time_text": str(appointment["time"]),
                "status": new_status,
            },
            daemon=True,
        ).start()
    except Exception:
        app.logger.exception("Could not start email notification.")

    return redirect(url_for("admin"))

# ==========================================
# ADMIN BULK DELETE
# ==========================================

@app.route("/admin/appointment/<int:appointment_id>/paid", methods=["POST"])
def mark_appointment_paid(appointment_id):
    if not admin_configured():
        return "Admin login is not configured.", 503

    paid_at = datetime.now(SHOP_TIMEZONE).isoformat(timespec="seconds")

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("admin_csrf_token", "")

    if (
        not saved_token
        or not hmac.compare_digest(submitted_token, saved_token)
    ):
        return "Invalid form token. Please reload the dashboard.", 400

    conn = get_db_connection()

    try:
        placeholder = "%s" if DATABASE_URL else "?"

        appointment = conn.execute(
            f"""
            SELECT service
            FROM appointments
            WHERE id = {placeholder}
              AND status = 'Accepted'
            """,
            (appointment_id,)
        ).fetchone()

        if appointment is None:
            conn.rollback()
            return (
                "Appointment not found or not eligible for payment. "
                "Please reload the dashboard.",
                409
            )

        paid_amount = SERVICE_PRICES.get(appointment["service"], 0)

        result = conn.execute(
            f"""
            UPDATE appointments
            SET status = 'Paid',
                paid_at = {placeholder},
                paid_amount = {placeholder}
            WHERE id = {placeholder}
              AND status = 'Accepted'
            """,
            (paid_at, paid_amount, appointment_id)
        )

        if result.rowcount == 0:
            conn.rollback()
            return (
                "Appointment not found or not eligible for payment. "
                "Please reload the dashboard.",
                409
            )

        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Appointment payment update failed.")
        return "Could not record payment. Please try again.", 500

    finally:
        conn.close()

    session.pop("admin_csrf_token", None)
    return redirect(url_for("admin"))

@app.route("/admin/appointments/delete", methods=["POST"])
def delete_selected_appointments():
    if not admin_configured():
        return "Admin login is not configured.", 503

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("admin_csrf_token", "")

    if (
        not saved_token
        or not hmac.compare_digest(submitted_token, saved_token)
    ):
        return "Invalid form token. Please reload the dashboard.", 400

    raw_ids = request.form.getlist("appointment_ids")

    appointment_ids = []

    for raw_id in raw_ids:
        try:
            appointment_id = int(raw_id)
            if appointment_id > 0 and appointment_id not in appointment_ids:
                appointment_ids.append(appointment_id)
        except (ValueError, TypeError):
            continue

    if not appointment_ids:
        session.pop("admin_csrf_token", None)
        return redirect(url_for("admin"))

    conn = get_db_connection()

    try:
        placeholder = "%s" if DATABASE_URL else "?"
        placeholders = ", ".join(
            [placeholder] * len(appointment_ids)
        )

        conn.execute(
            f"DELETE FROM appointments WHERE id IN ({placeholders})",
            tuple(appointment_ids)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Bulk appointment deletion failed.")
        return "Could not delete appointments. Please try again.", 500

    finally:
        conn.close()

    session.pop("admin_csrf_token", None)
    return redirect(url_for("admin"))

# ==========================================
# EDIT APPOINTMENT
# ==========================================

@app.route(
    "/admin/appointment/<int:appointment_id>/edit",
    methods=["GET", "POST"]
)
def edit_appointment(appointment_id):
    if not admin_configured():
        return "Admin login is not configured.", 503

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        submitted_token = request.form.get("csrf_token", "")
        saved_token = session.get("admin_csrf_token", "")

        if (
            not saved_token
            or not hmac.compare_digest(submitted_token, saved_token)
        ):
            return "Invalid form token. Please reload the dashboard.", 400

    conn = get_db_connection()

    try:
        placeholder = "%s" if DATABASE_URL else "?"

        if request.method == "POST" and not DATABASE_URL:
            conn.execute("BEGIN IMMEDIATE")

        appointment = conn.execute(
            f"""
            SELECT id, name, phone, service, barber, date, time, status
            FROM appointments
            WHERE id = {placeholder}
              AND status IN ('Pending', 'Accepted')
            """,
            (appointment_id,)
        ).fetchone()

        if appointment is None:
            return (
                "Appointment not found or cannot be edited. "
                "Paid and rejected appointments are locked.",
                409
            )

        appointment = dict(appointment)
        appointment["date"] = str(appointment["date"])[:10]
        appointment["time"] = str(appointment["time"])[:5]

        if request.method == "GET":
            return render_template(
                "edit_appointment.html",
                appointment=appointment,
                barbers=sorted(ALLOWED_BARBERS),
                csrf_token=session.get("admin_csrf_token")
            )

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        barber = request.form.get("barber", "").strip()
        date_text = request.form.get("date", "").strip()
        time_text = request.form.get("time", "").strip()

        updated = dict(appointment)
        updated.update({
            "name": name,
            "phone": phone,
            "service": service,
            "barber": barber,
            "date": date_text,
            "time": time_text
        })

        def edit_error(message):
            return render_template(
                "edit_appointment.html",
                appointment=updated,
                barbers=sorted(ALLOWED_BARBERS),
                csrf_token=session.get("admin_csrf_token"),
                error=message
            ), 400

        if not all([name, phone, service, barber, date_text, time_text]):
            return edit_error("Please complete all fields.")

        if len(name) > 100 or len(phone) > 20:
            return edit_error("Please check the name and phone number.")

        if service not in SERVICE_DURATIONS:
            return edit_error("Please select a valid service.")

        if barber not in ALLOWED_BARBERS:
            return edit_error("Please select a valid barber.")

        try:
            appointment_date = date.fromisoformat(date_text)
            parsed_time = datetime.strptime(
                time_text, "%H:%M"
            ).time()

            if appointment_date.isoformat() != date_text:
                raise ValueError("Invalid date format")

        except ValueError:
            return edit_error(
                "Please enter a valid appointment date and time."
            )

        now = datetime.now(SHOP_TIMEZONE)

        start = datetime.combine(
            appointment_date,
            parsed_time,
            tzinfo=SHOP_TIMEZONE
        )

        duration = SERVICE_DURATIONS[service]
        end = start + timedelta(minutes=duration)

        if start < now:
            return edit_error(
                "Please choose a future appointment time."
            )

        if (
            parsed_time < OPENING_TIME
            or end.date() != appointment_date
            or end.time().replace(tzinfo=None) > CLOSING_TIME
        ):
            return edit_error(
                "The appointment must start at or after 07:00 "
                "and finish by 23:00."
            )

        existing_appointments = conn.execute(
            f"""
            SELECT service, time
            FROM appointments
            WHERE barber = {placeholder}
              AND date = {placeholder}
              AND id != {placeholder}
            """,
            (barber, date_text, appointment_id)
        ).fetchall()

        for existing in existing_appointments:
            existing_time_text = str(existing["time"])[:5]

            existing_start_time = datetime.strptime(
                existing_time_text, "%H:%M"
            ).time()

            existing_start = datetime.combine(
                appointment_date,
                existing_start_time,
                tzinfo=SHOP_TIMEZONE
            )

            existing_duration = SERVICE_DURATIONS.get(
                existing["service"], 60
            )

            existing_end = existing_start + timedelta(
                minutes=existing_duration
            )

            if start < existing_end and existing_start < end:
                return edit_error(
                    "That time is unavailable for this barber. "
                    "Please choose another time."
                )

        result = conn.execute(
            f"""
            UPDATE appointments
            SET name = {placeholder},
                phone = {placeholder},
                service = {placeholder},
                barber = {placeholder},
                date = {placeholder},
                time = {placeholder}
            WHERE id = {placeholder}
              AND status IN ('Pending', 'Accepted')
            """,
            (
                name,
                phone,
                service,
                barber,
                date_text,
                time_text,
                appointment_id
            )
        )

        if result.rowcount != 1:
            conn.rollback()
            return "Appointment could not be updated.", 409

        conn.commit()

        session.pop("admin_csrf_token", None)

        return redirect(url_for("admin"))

    except Exception:
        conn.rollback()
        app.logger.exception("Appointment editing failed.")
        return "Could not update the appointment. Please try again.", 500

    finally:
        conn.close()


# ==========================================
# ADMIN LOGOUT
# ==========================================

@app.route("/logout", methods=["POST"])
def logout():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    session.clear()
    return redirect(url_for("login"))


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
