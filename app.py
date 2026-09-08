import uuid
from flask import Flask, render_template, request
from pipeline import run_pipeline

app = Flask(__name__)


@app.route("/submit", methods=["GET", "POST"])
def submit():
    submitted = False
    ticket_id = None
    name = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()

        if body:
            ticket_id = f"T-{uuid.uuid4().hex[:8]}"
            run_pipeline(ticket_id=ticket_id, subject=subject, body=body)
            submitted = True

    return render_template("submit.html", submitted=submitted, ticket_id=ticket_id, name=name)


@app.route("/agent-dashboard", methods=["GET", "POST"])
def agent_dashboard():
    result = None
    error = None

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        ticket_id = request.form.get("ticket_id", "").strip() or "T-MANUAL"

        if not body:
            error = "Please enter a ticket body before submitting."
        else:
            try:
                result = run_pipeline(ticket_id=ticket_id, subject=subject, body=body)
            except Exception as e:
                error = f"Something went wrong processing this ticket: {e}"

    return render_template("agent_dashboard.html", result=result, error=error)


@app.route("/")
def home():
    return (
        '<h2>Support Triage Agent</h2>'
        '<p><a href="/submit">Customer: Submit a ticket</a></p>'
        '<p><a href="/agent-dashboard">Agent: Open dashboard</a></p>'
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)