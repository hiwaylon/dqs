import json
import os
import shelve
import time
import unittest

import server


_ORIGINAL_DATASTORE = server._datastore


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self._db = shelve.open("testingdb")
        self._db["scores"] = []
        server._datastore = self._db

        server.app.config["TESTING"] = True

        self.app = server.app.test_client()

    def tearDown(self):
        server._datastore = _ORIGINAL_DATASTORE
        os.unlink("testingdb.db")

    def test_correct_score(self):
        response = self.app.post("/scores", data=json.dumps({
            "foodType": "fruit",
            "portions": 1,
            "date": 20130112
        }))

        self.assertEqual(json.loads(response.data), {"score": 2})

    def test_adds_daily_food_count(self):

        response = self.app.post("/scores", data=json.dumps({
            "foodType": "fruit",
            "portions": 1,
            "date": 20130113
        }))

        self.assertEqual(201, response.status_code)

        scores = self._db["scores"]

        #
        # TODO: Probably going into server library.
        #
        def find_if(collection, callback):
            for element in collection:
                if callback(element):
                    return element

            return None

        score = find_if(scores, lambda score: score["date"] == 20130113)

        self.assertNotEqual(None, score)
        self.assertEqual("fruit", score["foodType"])
        self.assertEqual(2, score["score"])

    def test_only_add_valid_food(self):
        response = self.app.post(
            "/scores", data=json.dumps({
                "foodType": "coffee",
                "portions": 3,
                "date": 20130202
            }))

        self.assertEqual(400, response.status_code)

        response = self.app.post(
            "/scores", data=json.dumps({
                "foodType": "vegetable",
                "portions": 1,
                "date": 20130203
            }))

        self.assertEqual(201, response.status_code)

    def test_valid_food_type(self):
        food_types = {
            "cookies": [],
            "milk": []
        }

        self.assertTrue(server._valid_food_type(food_types, "cookies"))
        self.assertFalse(server._valid_food_type(food_types, "cake"))

    def test_dqs_scores(self):
        #
        # TODO: Remove the portions parameter. Otherwise you would have to
        # return an array of score which the user would have to manager and
        # that sucks.
        #
        response = self.app.post(
            "/scores", data=json.dumps({
                "foodType": "vegetable",
                "portions": 1,
                "date": 20130203
            }))

        response = json.loads(response.data)
        self.assertEqual(2, response["score"])

    def test_score_should_match_portion(self):
        scores_for_portions = [2, 2, 2, 1, 0, 0]
        for score in scores_for_portions:
            response = self.app.post(
                "/scores", data=json.dumps({
                    "foodType": "vegetable",
                    "portions": 1,
                    "date": time.strftime("%Y%m%d")
                }))

            response = json.loads(response.data)
            self.assertEqual(response["score"], score)
