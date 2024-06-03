from flask import Flask, render_template, request, redirect, url_for
from database import (
    db,
    MessageTemplate,
    ScheduledMessage,
    IncomingMessage,
    CustomerInfo,
    Settings,
)
from message_scheduler import schedule_messages, schedule_incoming_message_checks
from datetime import datetime, date
import schedule
import time
import threading

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///messages.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=run_scheduler, daemon=True).start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/templates", methods=["GET", "POST"])
def templates():
    if request.method == "POST":
        name = request.form["name"]
        content = request.form["content"]
        new_template = MessageTemplate(name=name, content=content)
        db.session.add(new_template)
        db.session.commit()
        return redirect(url_for("templates"))

    templates = MessageTemplate.query.all()
    return render_template("templates.html", templates=templates)


@app.route("/schedule", methods=["GET", "POST"])
def schedule_message():
    if request.method == "POST":
        phone_number = request.form["phone_number"]
        message = request.form["message"]
        send_time = request.form["send_time"]
        new_message = ScheduledMessage(
            phone_number=phone_number, message=message, send_time=send_time
        )
        db.session.add(new_message)
        db.session.commit()
        schedule_messages()
        return redirect(url_for("schedule_message"))

    messages = ScheduledMessage.query.all()
    return render_template("messages.html", messages=messages)


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        check_interval = int(request.form["check_interval"])
        setting = Settings.query.first()
        if not setting:
            setting = Settings(check_interval=check_interval)
            db.session.add(setting)
        else:
            setting.check_interval = check_interval
        db.session.commit()
        schedule_incoming_message_checks()
        return redirect(url_for("settings"))

    setting = Settings.query.first()
    return render_template("settings.html", setting=setting)


@app.route("/customer_info")
def customer_info():
    view = request.args.get("view", "all")
    if view == "today":
        customers = CustomerInfo.query.filter(
            CustomerInfo.date_received >= date.today()
        ).all()
    else:
        customers = CustomerInfo.query.all()
    return render_template("customer_info.html", customers=customers, view=view)


@app.route("/incoming_messages")
def incoming_messages():
    messages = IncomingMessage.query.all()
    return render_template("incoming_messages.html", messages=messages)


@app.route("/send_reply", methods=["GET", "POST"])
def send_reply():
    if request.method == "POST":
        template_id = request.form["template"]
        template = MessageTemplate.query.get(template_id)
        customers = CustomerInfo.query.all()
        for customer in customers:
            send_message(customer.phone_number, template.content)
        return redirect(url_for("customer_info"))

    templates = MessageTemplate.query.all()
    return render_template("send_reply.html", templates=templates)


if __name__ == "__main__":
    with app.app_context():
        schedule_messages()
        schedule_incoming_message_checks()
    app.run(debug=True)
