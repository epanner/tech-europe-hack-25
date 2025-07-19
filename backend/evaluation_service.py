import os
from openai import OpenAI
from models import GdprParagraphList

from dotenv import load_dotenv
load_dotenv()

class EvaluationService:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAI API key is not provided.")
        self.openai = OpenAI(api_key=api_key)


    def get_evaluation(self, case_description):

        articles ="Art. 5 and 10 GDPR"
        try:
            prompt = f"""Our company had a data breach. Here's what happend: {case_description}. Please calculate the probability of us violating the following GDPR articles: {articles} and the approximate fine that we can expect. For each paragraph, assign the fitting classificcation. """

            response = self.openai.responses.parse(
                model="gpt-4o-2024-08-06",
                tools=[{
                    "type": "web_search_preview",
                    "search_context_size": "low",
                }],
                input=[
                    {"role": "system", "content": "You are an GDPR Expert that can help asses the risk of data breaches."},
                    {"role": "user", "content": prompt}
                ],
                text_format=GdprParagraphList,
            )
            return response.output_parsed

        except Exception as e:
            print(f"An error occured")
            return None