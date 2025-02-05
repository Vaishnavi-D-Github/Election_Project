from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Load data from JSON file
def load_data():
    with open("database.json", "r") as file:
        return json.load(file)

# Save data to JSON file
def save_data(data):
    with open("database.json", "w") as file:
        json.dump(data, file)

# Home Page (Election Commissioner)
@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", candidates=data["candidates"])

# Add Candidates Page
@app.route("/add_candidates", methods=["GET", "POST"])
def add_candidates():
    data = load_data()
    if request.method == "POST":
        num_candidates = int(request.form.get("num_candidates"))
        candidate_names = [request.form.get(f"candidate_{i}") for i in range(num_candidates)]

        # Update candidates in the database
        data["candidates"] = candidate_names
        save_data(data)
        return redirect(url_for("index"))

    return render_template("add_candidates.html")

# Voting Page
@app.route("/voting", methods=["GET", "POST"])
def voting():
    data = load_data()
    if not data["candidates"]:
        return "No candidates have been added yet. Please contact the election commissioner."

    if request.method == "POST":
        election_id = request.form.get("election_id")
        vote = int(request.form.get("vote"))

        # Check if voter already exists
        for voter in data["voters"]:
            if voter["id"] == election_id:
                if voter["voted"]:
                    return redirect(url_for("message_page", message="You have already voted."))
                else:
                    voter["voted"] = True
                    data["votes"].append(vote)
                    save_data(data)
                    return redirect(url_for("voting"))

        # Add new voter
        data["voters"].append({"id": election_id, "voted": True})
        data["votes"].append(vote)
        save_data(data)
        return redirect(url_for("voting"))

    return render_template("voting.html", candidates=data["candidates"])

@app.route('/message')
def message_page():
    message = request.args.get("message", "No message provided.")
    return render_template("message.html", message=message)

# Voter Status Page
@app.route("/status", methods=["GET", "POST"])
def status():
    data = load_data()
    if request.method == "POST":
        election_id = request.form.get("election_id")
        for voter in data["voters"]:
            if voter["id"] == election_id:
                if voter["voted"]:
                    return f"Election ID '{election_id}' has already voted."
                else:
                    return f"Election ID '{election_id}' has not voted yet."
        return f"Election ID '{election_id}' not found."

    return render_template("status.html")

# Results Page
@app.route("/results", methods=["GET", "POST"])
def results():
    data = load_data()
    vote_count = {candidate: 0 for candidate in data["candidates"]}
    for vote in data["votes"]:
        vote_count[data["candidates"][vote]] += 1

    if request.method == "POST":
        # Reset the database
        data["votes"] = []
        data["voters"] = []
        data["candidates"] = []
        save_data(data)
        return redirect(url_for("index"))

    return render_template("results.html", vote_count=vote_count)

if __name__ == "__main__":
    app.run(debug=True)