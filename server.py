import json
import logging
import os
import sqlite3
import time
import yaml

import flask

logger = logging.getLogger('dqs')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('dqs.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

app = flask.Flask(__name__)

with open('dqs.yaml') as fd:
    DIET_QUALITY_SCORE = yaml.load(fd)

DATASTORE_FILENAME = 'datastore'

connection = sqlite3.connect(DATASTORE_FILENAME)

# Wrap rows in dictionaries
connection.row_factory = sqlite3.Row

#
# TODO: Init script for Heroku??
#
db = connection.cursor()
try:
    db.execute(
        'CREATE TABLE scores (score int, food_type text, date int, meal_description text)')
except sqlite3.OperationalError:
    logger.info('scores table already exists')
#
#
#


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/scores', methods=['GET'])
def get_scores():
    # Have to make connection in the handler thread.
    #
    # TODO: Look in flask for how to do this as a hook.
    #
    connection = sqlite3.connect(DATASTORE_FILENAME)
    db = connection.cursor()
    scores_cursor = db.execute('select * from scores')

    scores = []
    for score in scores_cursor:
        logger.debug('got score: %s', score)
        scores.append(score)

    return json.dumps(scores)


@app.route('/scores', methods=['POST'])
def create_score():
    request = json.loads(flask.request.data)

    logger.info('Received request (%s).', request)

    date = request.get('date')
    if not date or len(str(date)) != 8:
        return (json.dumps({'error': 'Invalid or missing date.'}), 400)

    food_type = request.get('foodType')
    if not food_type:
        return (json.dumps({'error': 'Missing foodType.'}), 400)

    if not _valid_food_type(DIET_QUALITY_SCORE['diet_qualities'], food_type):
        return (json.dumps({'error': 'Invalid foodType.'}), 400)

    meal_description = request.get('meal_description')
    if not meal_description:
        return (json.dumps({'error': 'Missing meal_description.'}), 400)

    # Count serving of food type for day.
    today = time.strftime('%Y%m%d')

    def find_today(element):
        if element['date'] == today and element['foodType'] == food_type:
            return True

        return False

    # Have to make connection in the handler thread.
    #
    # TODO: Look in flask for how to do this as a hook.
    #
    connection = sqlite3.connect(DATASTORE_FILENAME)
    db = connection.cursor()

    # TODO: Inefficient, narrow the scores in the query, not in the filter.
    scores = db.execute('SELECT * FROM scores')
    todays_scores = filter(find_today, scores)

    # Compute the score for the given food and portions on this date.
    score = _get_current_score(food_type, len(todays_scores))

    logger.info('-- Adding score (%s).' % (score))

    db.execute(
        'INSERT INTO scores VALUES (%d, "%s", %d, "%s")' % (
            score, food_type, date, meal_description))

    return (json.dumps({
        'score': score
    }), 201)


def _get_current_score(food_type, portion):
    # food_type should have been validated at this point.
    food_scores = DIET_QUALITY_SCORE['diet_qualities'].get(food_type)

    logger.info(
        '-- Looking for portion (%s) for food (%s).' % (portion, food_type))

    if portion >= len(food_scores):
        return food_scores[-1]

    return food_scores[portion]


def _valid_food_type(food_types, food_type):
    valid_foods = [f for f in food_types]
    return food_type in valid_foods

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
