from flask import Blueprint, request, jsonify
import os
from evaluation_service import EvaluationService

evaluate_bp = Blueprint('gdpr_api', __name__, url_prefix='/api/')

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found when initializing ApiClient in gdpr_api.py")
else:
    api_client = EvaluationService(api_key=openai_api_key)

@evaluate_bp.route('/test', methods=['GET'])
def test():
    return jsonify("test"), 200


@evaluate_bp.route('/evaluate', methods=['POST'])
def evaluate_gdpr_breach():
    """
    API endpoint to evaluate a GDPR data breach case using OpenAI.
    Expects a JSON payload with a 'case_description' field.
    """
    if not api_client:
        return jsonify({"error": "API client not initialized. OpenAI API key missing."}), 500

    data = request.get_json()

    if not data or 'case_description' not in data:
        return jsonify({"error": "Missing 'case_description' in request body"}), 400

    case_description = data['case_description']

    evaluation_result = api_client.get_evaluation(case_description)
    
    if evaluation_result:
        try:
            return jsonify(evaluation_result.model_dump()), 200
        except:
            print("")
    else:
        return jsonify({"error": "Failed to get case evaluation from OpenAI API. Check server logs for details."}), 500