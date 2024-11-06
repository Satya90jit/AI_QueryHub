from transformers import pipeline
from app.services.nlp_service import DocumentIndexer

class DocumentRetriever:
    def __init__(self, index):
        self.index = index

    def retrieve(self, query, top_k=5):
        query_embedding = DocumentIndexer().embed_text(query)
        distances, indices = self.index.search(query_embedding, top_k)
        return indices, distances

class ResponseGenerator:
    def __init__(self, model_name="gpt2"):
        self.generator = pipeline("text-generation", model=model_name)

    def generate_response(self, context, query):
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        response = self.generator(prompt, max_length=200, num_return_sequences=1)
        return response[0]["generated_text"]

class RAGAgent:
    def __init__(self):
        self.indexer = DocumentIndexer()
        self.retriever = DocumentRetriever(self.indexer.index)
        self.generator = ResponseGenerator()

    def answer_query(self, query):
        indices, _ = self.retriever.retrieve(query)
        relevant_docs = [doc_content[idx] for idx in indices if idx != -1]
        context = " ".join(relevant_docs)
        
        if not context:
            return "No relevant documents found."
        
        return self.generator.generate_response(context, query)
