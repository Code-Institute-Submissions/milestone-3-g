import os
import requests
import json
from bs4 import BeautifulSoup
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


@app.route("/search_steam", methods=["GET", "POST"])
def search_steam():
    with open("/workspace/cpu_check/templates/game.html", 'r') as x:
        soup = BeautifulSoup(x, "html.parser")
        game = soup.find("button", class_="game_choice")
        game_id = game.get('data-id')
        return render_template("cpu.html", game_id=game_id)
   
    

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
