import json
import logging
import shelve
import time
import yaml

import flask

logger = logging.getLogger("dqs")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("dqs.log")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

app = flask.Flask(__name__)

with open("dqs.yaml") as fd:
    DIET_QUALITY_SCORE = yaml.load(fd)

# Preload shelve
DATASTORE_FILENAME = "datastore"
preload_data = [
    {
        "score": 2,
        "foodType": "vegetable",
        "date": 20130122
    },
    {
        "score": -1,
        "foodType": "fatty meat",
        "date": 20130124
    },
]

_datastore = shelve.open(DATASTORE_FILENAME)
_datastore.update({"scores": preload_data})


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/scores", methods=["GET"])
def get_scores():
    # User Python shelve for prototype data storage.
    scores = _datastore["scores"]
    logger.debug("datastore\n%s", scores)
    return json.dumps(scores)


@app.route("/scores", methods=["POST"])
def create_score():
    request = json.loads(flask.request.data)

    logger.info("Received request (%s).", request)

    date = request.get("date")
    if not date or len(str(date)) != 8:
        return (json.dumps({"error": "Invalid or missing date."}), 400)

    food_type = unicode(request.get("foodType"))
    if not food_type:
        return (json.dumps({"error": "Missing foodType."}), 400)

    if not _valid_food_type(DIET_QUALITY_SCORE["diet_qualities"], food_type):
        return (json.dumps({"error": "Invalid foodType."}), 400)

    # Compute the score for the given food and portions on this date.
    scores = _datastore["scores"]

    # Count serving of food type for day.
    today = time.strftime("%Y%m%d")

    def find_today(element):
        if element["date"] == today and element["foodType"] == food_type:
            return True

        return False

    todays_scores = filter(find_today, scores)
    score = _get_current_score(food_type, len(todays_scores))

    logger.info("-- Adding score (%s)." % (score))

    scores = _datastore["scores"]
    scores.append({
        "score": score,
        "date": date,
        "foodType": food_type,
    })
    _datastore["scores"] = scores

    return (json.dumps({"score": score}), 201)


def _get_current_score(food_type, portion):
    # food_type should have been validated at this point.
    food_scores = DIET_QUALITY_SCORE["diet_qualities"].get(food_type)

    logger.info(
        "-- Looking for portion (%s) for food (%s)." % (portion, food_type))

    if portion >= len(food_scores):
        return food_scores[-1]
    return food_scores[portion]


def _valid_food_type(food_types, food_type):
    valid_foods = [f for f in food_types]
    return food_type in valid_foods

if __name__ == "__main__":
    app.run(port=8000, debug=True)
