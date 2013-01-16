
import json
# import os
import unittest
# import tempfile

import pymongo

import server


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        # self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        connection = pymongo.MongoClient("localhost", 27017)
        self.db = connection.dqs
        server.app.config["TESTING"] = True
        self.app = server.app.test_client()

    def tearDown(self):
        # os.close(self.db_fd)
        # os.unlink(flaskr.app.config['DATABASE'])
        self.db.drop_collection("scores")

    def test_correct_score(self):
        response = self.app.post("/scores", data=json.dumps({
            "foodType": "fruit",
            "portions": 1,
            "date": "2013-01-12"
        }))

        print(response.data)

        assert json.loads(response.data) == {"score": 1}

    def test_adds_daily_food_count(self):
        self.app.post("/scores", data=json.dumps({
            "foodType": "fruit",
            "portions": 1,
            "date": "2013-01-13"
        }))

        scores_collection = self.db["scores"]

        score = scores_collection.find_one({"date": "2013-01-13"})

        print score

        assert None != score
        assert "fruit" == score["food_type"]
        assert 1 == score["score"]
