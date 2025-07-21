import pandas as pd 
import sqlite3
import os
import weaviate
from openai import OpenAI
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure
from unstructured.partition.pdf import partition_pdf
from dotenv import load_dotenv

def extract_paragraphs_from_pdf(pdf_file_name):
    pdf_file_name = os.path.join("verdicts", pdf_file_name)
    elements = partition_pdf(filename=pdf_file_name)

    # Combine text elements into paragraphs
    paragraphs = []
    current_paragraph = ""
    
    for el in elements:
        if el.category in ["NarrativeText", "ListItem"]:
            current_paragraph += " " + el.text.strip()
        else:
            # End of a paragraph; append if any content
            if current_paragraph.strip():
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""

            # Non-narrative (e.g., Title, List) — can be a new paragraph
            #if el.text.strip():
            #    paragraphs.append(el.text.strip())

    # Catch any remaining paragraph
    if current_paragraph.strip():
        paragraphs.append(current_paragraph.strip())

    return paragraphs

def translate_spanish_to_english(client: OpenAI, spanish_text):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a translator that translates Spanish to English."},
            {"role": "user", "content": f"Translate this to English: {spanish_text}"}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip() 

def main():
    print("Extracting text from PDF...")
    connect_obj = sqlite3.connect("spain_gdpr_fines_with_labels.db")
    query = "SELECT * FROM fines"
    df = pd.read_sql_query(query, connect_obj)
    
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    weaviate_client = weaviate.connect_to_weaviate_cloud(
                        cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
                        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
                    )

    
    # Create collection with OpenAI embeddings (if not exists)
    collection_name = "Documents"
    if not weaviate_client.collections.exists(collection_name):
        weaviate_client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        )

    # Get collection
    collection = weaviate_client.collections.get(collection_name)

    for _, row in df.iterrows():
        meta_data = row.to_dict()
        paragraphs = extract_paragraphs_from_pdf(row['verdict_link'].split('/')[-1])
        for paragraph in paragraphs:
            translated_paragraph = translate_spanish_to_english(openai_client, paragraph)
            print(translated_paragraph)
            print('\n')
        break

if __name__ == "__main__":
    load_dotenv()
    weaviate_client = weaviate.connect_to_weaviate_cloud(
                        cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
                        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY"))
                    )

    main()
