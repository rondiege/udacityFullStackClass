import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        """
        After request is received, add headers and allow the following methods
        """
        response.headers.add('Access-Control-Allow', 'Content-Type, ''Authorization')
        response.headers.add('Access-Control-Allow', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

  def paginate(request, selection):
	  page = request.args.get('page', 1, type=int)
	  start =  (page - 1) * QUESTIONS_PER_PAGE
	  end = start + QUESTIONS_PER_PAGE

	  questions = [question.format() for question in selection]
	  current_questions = questions[start:end]

	  return current_questions

  '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
	  categories = Category.query.all()

	  categories = {category.id: category.type for category in categories}

	  return jsonify({
		  'success': True,
		  'categories' : categories,
		  'total_categories' : len(categories)
	})

  '''
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  '''
  @app.route('/questions', methods=['GET'])
  def get_all_questions():
	  page = request.args.get('page', 1, type=int)
	  questions = Question.query.all()

	  selectedQuestion = paginate(request, questions)

	  categories = Category.query.all()
	  formatted_cat = {category.id: category.type for category in categories}

	  return jsonify({
		  'success': True,
		  'questions' : selectedQuestion,
		  'total_questions' : len(questions),
		  'categories' : formatted_cat,
		  'current_category': None
	})

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
	  print(request.get_json())
	  sys.stdout.flush()
	  body = request.get_json()

	  question = body.get('question', None)
	  answer = body.get('answer', None)
	  difficulty = body.get('difficulty', None)
	  category = body.get('category', None)

	  success = True
	  try:
		  question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
		  question.insert()
	  except:
		  # db.session.rollback()
		  sucess = False
		  print(sys.exc_info())
		  sys.stdout.flush()
		  abort(422, description="Unprocessable\n"+sys.exc_info())

	  # finally:
		  # db.session.close()

	  selection = Question.query.order_by(Question.id).all()
	  current_questions = paginate(request, selection)

	  return jsonify({
		'success': True,
		'created': question.id,
		'questions': current_questions,
		'total_questions': len(Question.query.all())
	  })

  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''


  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

  return app
