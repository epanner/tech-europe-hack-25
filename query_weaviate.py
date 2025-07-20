import os
import weaviate
from weaviate.classes.init import Auth
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    weaviate_client = weaviate.connect_to_weaviate_cloud(
                        cluster_url=os.getenv("WEAVIATE_CLUSTER_URL"),
                        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_API_KEY")),
                        headers={'X-OpenAI-Api-key': os.getenv("OPENAI_KEY")},
                    )

    precedent = weaviate_client.collections.get("Precedent")
    
    test_case = "A company in the telecommunication sector had a data breach. They failed to communicate about the breach to their costumers on time. what kind of gdpr penalties would be levied against them ?"

    # Query using summary vector
    response_summary = precedent.query.near_text(
        query=test_case,
        target_vector="summary_vector",
        limit=10,
        return_metadata=["score"]
    )

    # Query using chunk vector
    response_chunk = precedent.query.near_text(
        query=test_case,
        target_vector="chunk_vector", 
        limit=10,
        return_metadata=["score"]
    )

    # Hybrid query combining both vectors
    response_hybrid = precedent.query.hybrid(
        query=test_case,
        target_vector="summary_vector",  # Primary vector
        limit=10,
        return_metadata=["score"]
    )

    # Print results
    print("Summary-based results:")
    for obj in response_summary.objects:
        print(f"Score: {obj.metadata.score:.4f}")
        print(f"Company: {obj.properties['company']}")
        print(f"Summary: {obj.properties['summary'][:200]}...")
        print("---")

    print("\nChunk-based results:")
    for obj in response_chunk.objects:
        print(f"Score: {obj.metadata.score:.4f}")
        print(f"Company: {obj.properties['company']}")
        print(f"Chunk: {obj.properties['chunk'][:200]}...")
        print("---")
    
    print("\nHybrid Summary-based results:")
    for obj in response_hybrid.objects:
        print(f"Score: {obj.metadata.score:.4f}")
        print(f"Company: {obj.properties['company']}")
        print(f"Chunk: {obj.properties['chunk'][:200]}...")
        print("---")

    weaviate_client.close()
