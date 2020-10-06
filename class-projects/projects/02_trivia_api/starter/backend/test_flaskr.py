import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
import sys


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {"answer":"Habari",
                             "question": "What is an Swahili greeeting?",
                             "difficulty": 1,
                             "category": 2}

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        results = self.client().get('/categories')
        data = json.loads(results.data)

        print(data)
        sys.stdout.flush()

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_get_questions(self):
        results = self.client().get('/questions')
        data = json.loads(results.data)

        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_add_and_delete_question_success(self):
        create_results = self.client().post('/questions', json=self.new_question)
        data = json.loads(create_results.data)

        self.assertEqual(create_results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

        question_id = data['created']
        total_questions = data['total_questions']

        delete_results = self.client().delete('/questions/'+str(question_id))
        data = json.loads(delete_results.data)

        self.assertEqual(create_results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], total_questions-1)

    def test_422_failed_add_question(self):
        create_results = self.client().post('/questions', json={})
        self.assertEqual(create_results.status_code, 422)

    def test_422_delete_question_fail(self):
        delete_results = self.client().delete('/questions/555555555')
        self.assertEqual(delete_results.status_code, 422)

    def test_search_questions(self):
        search_results = self.client().post('/questions/searches', json={"searchTerm":"title"})
        data = json.loads(search_results.data)

        self.assertEqual(search_results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_search_question_not_found(self):
        search_results = self.client().post('/questions/searches', json={"searchTerm":"sdfhajsdhfla"})
        self.assertEqual(search_results.status_code, 404)

    def test_quizzes(self):
        category = 1

        search_results = self.client().post('/quizzes', json={"quiz_category":{"id":1}, "previous_questions":[]})
        data = json.loads(search_results.data)

        self.assertEqual(search_results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertFalse(data['previous_questions'])
        self.assertEqual(data['quiz_category']['id'], category)

        question_id = data['question']['id']

        search_results = self.client().post('/quizzes', json={"quiz_category":{"id":1}, "previous_questions":[question_id]})
        data = json.loads(search_results.data)

        self.assertEqual(search_results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['previous_questions'], [question_id])
        self.assertEqual(data['quiz_category']['id'], category)




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
