from flask import Flask, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    app = Flask(__name__)
    #  implent cors of all of the /api/ enpdoin and allows all origins
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# decorator means after request is recived run this method - This will make it so all endpoints have this.
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Method', 'GET, POST, PATCH, DELETE, OPTIONS')

    @app.route('/')
    def hello():
        return jsonify({"message": "hello. I love you."})

    @app.route('/smile')
    def smile():
        return ':)'

    @app.route('/messages')
    # enabling cors specifially for this endpoint
    # @cross_origin()
    def get_messages():
        return 'GETTING MESSAGES'

    return app
