import PyPDF2
import openai
import os
import sqlite3
import pandas as pd
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class GDPRViolationClassification(BaseModel):
    lawfulness_of_processing: str
    data_subject_rights_compliance: str
    risk_management_and_safeguards: str
    accountability_and_governance: str

# === SETTINGS ===
openai.api_key = os.getenv("OPENAI_KEY")

# === STEP 1: Read PDF text ===
def extract_text_from_pdf(pdf_file_name):
    text = ""
    pdf_file_name = os.path.join("verdicts", pdf_file_name)
    if os.path.isfile(pdf_file_name): 
        with open(pdf_file_name, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            if len(reader.pages) <= 50:
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    print(extracted_text)
                    text += extracted_text
    return text

def classify_gdpr_violation(prompt):
    response = openai.responses.parse(
                model="gpt-4o-2024-08-06",
                input=[
                    {"role": "system", "content": "You are a helpful AI assistant. You are required to read a GDRP violation case verdict in spanish and assess the case"},
                    {"role": "user", "content": prompt}
                ],
                text_format=GDPRViolationClassification,
            )
    print(response.output_parsed)

# === MAIN PIPELINE ===
def main():
    print("🔍 Extracting text from PDF...")
    connector_obj = sqlite3.connect("spain_gdpr_fines_gdpr.db")
    query = "SELECT * FROM fines"
    df = pd.read_sql_query(query, connector_obj)
    for _, row in df.iterrows():
        file_name = row['verdict_link'].split('/')[-1]
        if file_name.split('.')[-1] == "pdf":
            spanish_text = extract_text_from_pdf(file_name)
            if spanish_text != "":
                prompt = f"""
                Analyze the following case report and assign one label from each of the following four GDPR violation characteristics.

                The 4 characteristics are:
                1. Lawfulness of Processing
                    - lawful_and_appropriate_basis
                    - lawful_but_principle_violation
                    - no_valid_basis
                    - exempt_or_restricted

                2. Data Subject Rights Compliance
                    - full_compliance
                    - partial_compliance
                    - non_compliance
                    - not_triggered

                3. Risk Management and Safeguards
                    - proactive_safeguards
                    - reactive_only
                    - insufficient_protection
                    - not_applicable

                4. Accountability and Governance
                    - fully_accountable
                    - partially_accountable
                    - not_accountable
                    - not_required

                Case:
                {spanish_text}
                """

                print("🤖 Classifying GDPR violations...")
                labels = classify_gdpr_violation(prompt)
                print("\n📊 Assigned Labels:\n", labels)
        break

if __name__ == "__main__":
    main()
