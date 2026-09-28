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
    assert b"Make an Appointment" in response.data


def test_successful_booking():
    client = app.test_client()

    response = client.post(
        "/book",
        data={
            "name": "John",
            "email": "john@example.com",
            "service": "Haircut",
            "barber": "Alex",
            "date": "2026-10-01",
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
