import json
import yaml

import flask
import pymongo

app = flask.Flask(__name__)


with open("dqs.yaml") as fd:
    DIET_QUALITY_SCORE = yaml.load(fd)

connection = pymongo.MongoClient("localhost", 27017)
DB = connection.dqs


@app.route("/scores", methods=["POST"])
def scores():
    request = json.loads(flask.request.data)

    date_string = request.get("date")
    if not date_string:
        return json.dumps({"error": "Missing date."})

    food_type = request.get("foodType")
    if not food_type:
        return json.dumps({"error": "Missing foodType."})

    portions = request.get("portions")
    if not portions:
        return json.dumps({"error": "Invalid or mssing portions."})

    # Compute the score for the given food and portions on this date.
    score = _get_current_score(food_type, date_string, portions)

    scores_collection = DB["scores"]
    scores_collection.insert({
        "score": score,
        "date": date_string,
        "food_type": food_type,
        "portions": portions
    })

    return json.dumps({"score": score})


def _get_current_score(food_type, date, portions):
    # food_scores = DIET_QUALITY_SCORE["diet_qualities"].get(food_type)
    # score = food_scores[daily_portion]
    return 1

if __name__ == "__main__":
    app.run()
