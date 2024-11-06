import faiss
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

class DocumentIndexer:
    def __init__(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.model = AutoModel.from_pretrained(embedding_model)
        self.index = faiss.IndexFlatL2(384)  # Ensure this matches the embedding dimension

    def embed_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state.mean(dim=1)
        return embeddings.cpu().numpy()

    def index_document(self, document_texts):
        embeddings = np.vstack([self.embed_text(text) for text in document_texts])
        self.index.add(embeddings)
        print(f"Indexed {self.index.ntotal} documents.")  # Debug: Check number of documents indexed

    def query_document(self, query: str, threshold=1e-2):  # Adjusted threshold for relevance
        query_embedding = self.embed_text(query)
        print(f"Query embedding shape: {query_embedding.shape}")  # Debug: Ensure shape is (1, 384)

        if self.index.ntotal == 0:
            print("No documents in the index.")  # Debug: No documents indexed
            return {"message": "No documents indexed."}

        D, I = self.index.search(query_embedding, k=5)
        print(f"Search results: {D}, {I}")  # Debug: Check raw search results

        similarity_scores = D.flatten()
        document_ids = I.flatten()

        relevant_results = [{"doc_id": int(doc_id), "score": float(score)} 
                            for doc_id, score in zip(document_ids, similarity_scores) if score > threshold]

        if relevant_results:
            return relevant_results
        else:
            return {"message": "No relevant documents found"}
