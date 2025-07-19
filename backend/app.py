from dotenv import load_dotenv
from flask import Flask
from api.endpoints import evaluate_bp
print("-----   Starting app   -----")

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(evaluate_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)