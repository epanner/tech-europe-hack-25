import os

from flask import Flask
from evaluation_service import EvaluationService
from api.evaluation import evaluate_bp
from dotenv import load_dotenv
from flask_cors import CORS  # Add this import

print("-----   Starting test   -----")

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

api_client = EvaluationService(api_key)

case_description = "A couple of user mails got leaked in the darknet because our database was publicly accessible"

case_evaluation = api_client.get_evaluation(case_description)

print(case_evaluation)

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins
    app.register_blueprint(evaluate_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)