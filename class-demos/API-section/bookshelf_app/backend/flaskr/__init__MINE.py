import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random
import sys

from models import setup_db, Book

BOOKS_PER_SHELF = 8
app = Flask(__name__)
setup_db(app)
CORS(app)
db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404

@app.errorhandler(422)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable... for now"
        }), 422

def paginate_books(request, selection):
    # get page make it an int, if none default to 1
    page = request.args.get('page', 1, type=int)
    start = (page -1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    formatted_books = [b.format() for b in selection]
    current_books = formatted_books[start:end]

    return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.

# def create_app(test_config=None):
  # create and configure the app


  # CORS Headers

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # @TODO: Write a route that retrivies all books, paginated.
  #         You can use the constant above to paginate by eight books.
  #         If you decide to change the number  of books per page,
  #         update the frontend to handle additional books in the styling and pagination
  #         Response body keys: 'success', 'books' and 'total_books'
  # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
@app.route('/books', methods=['GET'])
def get_all_books():
    books = Book.query.all()

    page = request.args.get('page', 1, type=int)
    start = (page -1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    formatted_books = [b.format() for b in books]

    if len(formatted_books) == 0:
        abort(404)

    # return formatted_books
    return jsonify({
        'success': True,
        'books' : formatted_books,
        'total_books' : len(formatted_books)
    })



  # @TODO: Write a route that will update a single book's rating.
  #         It should only be able to update the rating, not the entire representation
  #         and should follow API design principles regarding method and route.
  #         Response body keys: 'success'
  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
@app.route('/books/<int:book_id>', methods=['PATCH'])
def update_book(book_id):
    success = True
    try:
        body = request.get_json()
        if 'rating' in body:
            book = Book.query.get(book_id)

            if book is None:
                abort(404)

            book.rating = int(body.get('rating'))
            db.session.commit()
    except:
        db.session.rollback()
        success = False
        print(sys.exc_info())
    finally:
        db.session.close()

    return jsonify({"success":success})


  # @TODO: Write a route that will delete a single book.
  #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
  #        Response body keys: 'success', 'books' and 'total_books'

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    success = True
    try:
        book = Book.query.filter(Book.id == book_id).one_or_none()
        if book is None:
            abort(404)

        book.delete()

        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, selection)

        return jsonify({"success":success,
        "deleted": book_id,
        "books": current_books,
        "total_books": len(selection)})

    except:
        db.session.rollback()
        print(sys.exc_info())
        abort(422)

    return redirect(url_for('get_all_books', page=1))




  # @TODO: Write a route that create a new book.
  #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
  #       Your new book should show up immediately after you submit it at the end of the page.
@app.route('/books', methods=['POST'])
def add_book():
    success = True
    #  force true makes it so this will work even if the user doesn't set the mimetype
    title = request.get_json(force=True)['title']
    author = request.get_json()['author']
    rating = request.get_json()['rating']

    # or get
    # body = request.get_json()
    #  get the body or default to none
    # title = body.get('title', none)


    try:
        book = Book(title=title, author=author, rating=rating);
        db.session.add(book)
        db.session.commit()
    except:
        db.session.rollback()
        success = False
        print(sys.exc_info())
    finally:
        db.session.close()

    return  jsonify({"success" : success})


    return app
