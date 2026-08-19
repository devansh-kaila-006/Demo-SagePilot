import json
import os
import google.generativeai as genai
import numpy as np

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_products_orders.json")

def load_data():
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def get_embedding(text):
    if not os.environ.get("GEMINI_API_KEY"):
        return [0] * 768
    try:
        result = genai.embed_content(
            model="models/gemini-embedding-2",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        # Return a zero vector fallback just so the script doesn't completely crash if no API key
        return [0] * 768

class SimpleRAG:
    def __init__(self):
        self.data = load_data()
        self.documents = []
        self.embeddings = []
        self._prepare_corpus()
        
    def _prepare_corpus(self):
        # Index products
        for p in self.data.get("products", []):
            text = f"Product: {p['name']}. Category: {p['category']}. Description: {p['description']}. Price: {p['price']}."
            self.documents.append(text)
            
        # Index policies
        for k, v in self.data.get("policies", {}).items():
            text = f"Policy ({k}): {v}"
            self.documents.append(text)
            
        # Optional: In a real system, orders might be looked up via API rather than embedded,
        # but we embed them here for semantic retrieval of general order questions if needed.
        for o in self.data.get("orders", []):
            text = f"Order #{o['id']} by {o['customer']}. Status: {o['status']}. Total: {o['total_amount']}."
            self.documents.append(text)

        # Generate embeddings (this runs on startup for the demo)
        print("Generating embeddings for mock dataset...")
        for doc in self.documents:
            self.embeddings.append(get_embedding(doc))
        self.embeddings = np.array(self.embeddings)
        print("Embeddings generated.")

    def retrieve(self, query, top_k=3):
        # If API key is missing, fallback to returning all text
        if not os.environ.get("GEMINI_API_KEY"):
            return "\n".join(self.documents[:top_k])
            
        query_emb = get_embedding(query)
        if not query_emb:
            return ""
            
        query_emb = np.array(query_emb)
        
        # Cosine similarity
        similarities = []
        for doc_emb in self.embeddings:
            # handle zero vectors
            if np.linalg.norm(doc_emb) == 0 or np.linalg.norm(query_emb) == 0:
                similarities.append(0)
            else:
                sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
                similarities.append(sim)
                
        # Get top k
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append(self.documents[idx])
            
        return "\n".join(results)

# Singleton instance
rag_system = None

def get_rag():
    global rag_system
    if rag_system is None:
        rag_system = SimpleRAG()
    return rag_system
