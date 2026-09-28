from flask import Flask, render_template, request

app = Flask(__name__)


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

        return render_template(
            "confirmation.html",
            name=name,
            service=service,
            barber=barber,
            date=date,
            time=time
        )

    return render_template("booking.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
