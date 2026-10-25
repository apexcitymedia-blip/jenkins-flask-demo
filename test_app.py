import os
import tempfile
from datetime import date, timedelta

_test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_test_db.close()

os.environ.pop("DATABASE_URL", None)
os.environ["DATABASE_PATH"] = _test_db.name

from app import app

def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert b"BARBERBOOK" in response.data


def test_booking_page():
    client = app.test_client()
    response = client.get("/book")

    assert response.status_code == 200
    assert b"Reserve your" in response.data


def test_successful_booking():
    client = app.test_client()
    future_date = (date.today() + timedelta(days=7)).isoformat()

    response = client.post(
        "/book",
        data={
            "name": "John",
            "email": "john@example.com",
            "service": "Haircut",
            "barber": "Alex",
            "date": future_date,
            "time": "10:00",
        },
    )

    assert response.status_code == 200
    assert b"You're Booked, John!" in response.data


def test_incomplete_booking():
    client = app.test_client()

    response = client.post(
        "/book",
        data={
            "name": "John",
        },
    )

    assert response.status_code == 400
    assert b"Please complete all fields." in response.data


def test_booking_is_saved():
    client = app.test_client()
    future_date = (date.today() + timedelta(days=7)).isoformat()

    response = client.post(
        "/book",
        data={
            "name": "Jane",
            "email": "jane@example.com",
            "service": "Beard Trim",
            "barber": "Mike",
            "date": future_date,
            "time": "14:00",
        },
    )

    assert response.status_code == 200

    import sqlite3
    conn = sqlite3.connect(os.environ["DATABASE_PATH"])
    appointment = conn.execute(
        """
        SELECT name, email, service, barber, date, time
        FROM appointments
        WHERE name = ?
        """,
        ("Jane",)
    ).fetchone()
    conn.close()

    assert appointment == (
        "Jane",
        "jane@example.com",
        "Beard Trim",
        "Mike",
        future_date,
        "14:00",
    )
