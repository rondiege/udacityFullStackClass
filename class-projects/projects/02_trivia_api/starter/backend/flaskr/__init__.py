import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from  sqlalchemy.sql.expression import func
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

  # Set up CORS. Allow '*' for origins.
  CORS(app, resources={r"/*": {"origins": "*"}})

  # Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow', 'Content-Type, ''Authorization')
        response.headers.add('Access-Control-Allow', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

#  Does the pagination for questions
  def paginate(request, selection):
	  page = request.args.get('page', 1, type=int)
	  start =  (page - 1) * QUESTIONS_PER_PAGE
	  end = start + QUESTIONS_PER_PAGE

	  questions = [question.format() for question in selection]
	  current_questions = questions[start:end]

	  return current_questions

  # An endpoint to handle GET requestsfor all available categories.
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
  An endpoint that handles GET requests for questions,
  including pagination (every 10 questions).
  Returns a list of questions, number of total questions, current category, categories.
  '''
  @app.route('/questions', methods=['GET'])
  def get_all_questions():
	  questions = Question.query.all()

	  selectedQuestion = paginate(request, questions)

	  categories = Category.query.all()
	  formatted_cat = {category.id: category.type for category in categories}

	  return jsonify({'success': True,
					  'questions' : selectedQuestion,
					  'total_questions' : len(questions),
					  'categories' : formatted_cat,
					  'current_category': None})


  # An endpoint that allows DELETE of a question using a question ID.
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
	  try:
		  question = Question.query.filter(Question.id == question_id).one_or_none()

		  if question is None:
			  abort(404)

		  question.delete()

		  selection = Question.query.order_by(Question.id).all()
		  current_questions = paginate(request, selection)

		  return jsonify({
	        'success': True,
	        'deleted': question_id,
	        'questions': current_questions,
	        'total_questions': len(Question.query.all())
	      })

	  except:
		  abort(422, description="Unprocessable")

  '''
  An endpoint that allow POST of a new question, which requires the question
  and answer text, category, and difficulty score.
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
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
		  sucess = False
		  print(sys.exc_info())
		  sys.stdout.flush()
		  abort(422, description="Unprocessable")

	  selection = Question.query.order_by(Question.id).all()
	  current_questions = paginate(request, selection)

	  return jsonify({
		'success': True,
		'created': question.id,
		'questions': current_questions,
		'total_questions': len(Question.query.all())
	  })

  '''
  A POST endpoint to get questions based on a search term.
  It returns any questions for whom the search term
  is a substring of the question.
  '''
  @app.route('/questions/searches', methods=['POST'])
  def search_questions():

      body = request.get_json()
      term = body.get('searchTerm', None)

      questions = Question.query.filter(Question.question.ilike("%"+term+"%")).all()

      if len(questions) == 0:
          abort(404)

      selectedQuestion = paginate(request, questions)

      categories = Category.query.all()
      formatted_cat = {category.id: category.type for category in categories}

      return jsonify({"success": "True",
                      "questions": selectedQuestion,
                      "total_questions": len(questions),
                      "categories": formatted_cat,
                      "current_category": None})

  '''
  A GET endpoint to get questions based on category.
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
      questions = Question.query.filter(Question.category==category_id).all()

      if len(questions) == 0:
          abort(404)

      selectedQuestion = paginate(request, questions)

      return jsonify({'success': True,
                      'questions' : selectedQuestion,
                      'total_questions' : len(questions),
                      'current_category': category_id})

  '''
  A POST endpoint to get questions to play the quiz.
  This endpoint takes category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.
  '''
  @app.route('/quizzes', methods=['POST'])
  def take_quiz():
      body = request.get_json()
      category = body.get('quiz_category', None)
      prev_questions = body.get('previous_questions', None)

      question = Question.query

      # This means it is not any category, but a specific one
      # Also would be smart to verify the category exsits
      if category["id"] != 0:
          question = question.filter(Question.category == category["id"])

      if prev_questions:
          # generates a not in clause
          question = question.filter(~Question.id.in_(prev_questions))

      # first() returns None if there is nothing there to be selected
      question = question.order_by(func.random()).limit(1).first()

      if question is not None:
          return jsonify({"success": True,
                          "question": question.format(),
                          "previous_questions": prev_questions,
                          "quiz_category": category})
      else:
          return jsonify({"success": True,
                          "question": "Phew, good work. You answered all the questions in that categoty."
                                    + " Try another category!",
                          "previous_questions": previous_questions,
                          "quiz_category": quiz_category})

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({"success": False,
                      "error": 404,
                      "message": "Nope not here."}), 404

  @app.errorhandler(422)
  def not_found(error):
      return jsonify({"success": False,
                      "error": 422,
                      "message": error}), 422

  return app
