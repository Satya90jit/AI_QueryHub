# app/services/nlp_service.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.document import Document
from sqlalchemy.orm import Session

class NLPService:
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embeddings = {}  # Store document embeddings in memory
    documents = {}  # Store document contents by ID

    @classmethod
    def index_document(cls, doc_content: str, doc_id: int):
        """Indexes the document's content by generating its embedding."""
        try:
            # Generate an embedding for the document content
            embedding = cls.model.encode(doc_content)
            
            # Check if the embedding is valid
            if embedding is None or np.isnan(embedding).any() or len(embedding) == 0:
                print(f"Error: Invalid embedding for document: {doc_content}")
                return
            
            # Store the embedding and content with the document id as key
            cls.embeddings[doc_id] = embedding
            cls.documents[doc_id] = doc_content
            print(f"Document Indexed: {doc_content}")
        except Exception as e:
            print(f"Error indexing document: {e}")

    @classmethod
    def query_document(cls, query: str, db: Session, threshold=0.5):
        """Queries indexed documents to find the most relevant ones."""
        try:
            # Generate an embedding for the query
            query_embedding = cls.model.encode(query)
            
            if query_embedding is None or np.isnan(query_embedding).any() or len(query_embedding) == 0:
                print(f"Error: Invalid query embedding for query: {query}")
                return {"error": "Invalid query embedding"}
            
            # Calculate cosine similarities between the query and all indexed documents
            similarities = {}
            for doc_id, doc_embedding in cls.embeddings.items():
                sim = cosine_similarity([query_embedding], [doc_embedding])[0][0]
                similarities[doc_id] = sim

            # Sort documents by similarity score in descending order
            sorted_docs = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            
            if sorted_docs and sorted_docs[0][1] >= threshold:
                best_doc_id = sorted_docs[0][0]
                best_doc_content = cls.documents.get(best_doc_id, "Content not found")
                
                print(f"Found relevant document with ID: {best_doc_id} and similarity: {sorted_docs[0][1]}")
                
                # Fetch the actual document content from the database
                document = db.query(Document).filter(Document.id == best_doc_id).first()
                if document:
                    return {"document_id": document.id, "content": document.filename, "text": document.file_metadata}
                else:
                    return {"message": "Document not found in the database"}
            else:
                return {"message": "No relevant documents found"}
        except Exception as e:
            print(f"Error querying document: {e}")
            return {"error": str(e)}
