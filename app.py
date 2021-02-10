import os
import requests
import json
from re import search
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)



@app.route("/")
@app.route("/game")
def game():
    return render_template("game.html" )


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    game = list(mongo.db.game.find({"$text": {"$search": "\"" + query + "\""}}))
    return render_template("game.html", game=game)


@app.route("/search1", methods=["GET", "POST"])
def search1():
    query = request.form.get("query")
    game = list(mongo.db.cpu.find({"$text": {"$search": "\"" + query + "\""}}))
    return render_template("game.html", game=game)



@app.route('/submit', methods=["GET", "POST"])
def submit():
    game_id = format(request.form['text'])
    r = requests.get("https://store.steampowered.com/api/appdetails?appids=" + game_id + "")
    game=json.loads(r.text)[ game_id ]['data']['pc_requirements']['minimum']
    return render_template("cpu.html", game=game)


@app.route("/benchmark", methods=["GET", "POST"])
def benchmark():
    if request.method == "POST":
        # check if username already exists in db
        game_cpu_combo = request.form.get("name") + "_" + request.form.get("cpuName")
        existing_combo = mongo.db.cpu_game.find_one(
            {"cpu_game": (game_cpu_combo)})


        if existing_combo:
            flash("combo found")
            return redirect(url_for("benchmark"))


        cpu_game_combo = {
            "match_game": request.form.get("name") + "_" + request.form.get("cpuName")
        }
        mongo.db.match_game.insert_one(cpu_game_combo )

    return render_template("benchmark.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
