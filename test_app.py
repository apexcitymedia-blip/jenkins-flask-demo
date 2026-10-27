import sqlite3
from datetime import date, timedelta

import pytest

import app as barberbook


@pytest.fixture
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test_barberbook.db"

    monkeypatch.setattr(barberbook, "DATABASE_URL", None)
    monkeypatch.setattr(barberbook, "DATABASE", str(database_path))

    barberbook.init_db()

    return barberbook.app.test_client()


def future_date(days=7):
    return (date.today() + timedelta(days=days)).isoformat()


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"BARBERBOOK" in response.data


def test_booking_page(client):
    response = client.get("/book")

    assert response.status_code == 200
    assert b"Reserve your" in response.data


def test_successful_booking(client):
    booking_date = future_date()

    response = client.post(
        "/book",
        data={
            "name": "John",
            "email": "john@example.com",
            "service": "Haircut",
            "barber": "Alex",
            "date": booking_date,
            "time": "10:00",
        },
    )

    assert response.status_code == 200
    assert b"You're Booked, John!" in response.data


def test_incomplete_booking(client):
    response = client.post(
        "/book",
        data={"name": "John"},
    )

    assert response.status_code == 400
    assert b"Please complete all fields." in response.data


def test_booking_is_saved(client, tmp_path):
    booking_date = future_date(8)

    response = client.post(
        "/book",
        data={
            "name": "Jane",
            "email": "jane@example.com",
            "service": "Beard Trim",
            "barber": "Mike",
            "date": booking_date,
            "time": "14:00",
        },
    )

    assert response.status_code == 200

    conn = sqlite3.connect(barberbook.DATABASE)
    appointment = conn.execute(
        """
        SELECT name, email, service, barber, date, time
        FROM appointments
        WHERE name = ?
        """,
        ("Jane",),
    ).fetchone()
    conn.close()

    assert appointment == (
        "Jane",
        "jane@example.com",
        "Beard Trim",
        "Mike",
        booking_date,
        "14:00",
    )
