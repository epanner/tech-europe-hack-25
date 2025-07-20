import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv

load_dotenv()

# Best practice: store your credentials in environment variables
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
openai_api_key = os.environ["OPENAI_API_KEY"]

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
    headers={'X-OpenAI-Api-key': openai_api_key}
)

try:
    # Check connection
    print("Connected to Weaviate:", client.is_ready())
    
    # Get the Precedent collection
    collection = client.collections.get("Precedent")
    
    # Get the count of objects in the collection
    response = collection.aggregate.over_all(total_count=True)
    count = response.total_count
    
    print(f"Number of elements in Precedent collection: {count}")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    # Close the connection
    client.close()