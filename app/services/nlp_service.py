from sentence_transformers import SentenceTransformer
import faiss
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging
import traceback  # For better error handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Logging is configured properly.")

# Load the Sentence Transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
logger.info("SentenceTransformer model loaded successfully.")

# Initialize FAISS index
embedding_dim = embedding_model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(embedding_dim)  # L2 distance for similarity
documents = {}  # To store documents with IDs as keys for easy retrieval

# Embedding function
def create_embedding(text):
    return embedding_model.encode(text)

class NLPService:
    @staticmethod
    def initialize_rag_agent():
        """Initialize the RAG agent setup."""
        # Create a prompt template for query processing
        prompt_template = PromptTemplate(
            template="Generate a response based on this context: {context}",
            input_variables=["context"]
        )
        # Initialize the LLM chain (you can replace None with your actual model)
        llm_chain = LLMChain(llm=None, prompt=prompt_template)
        return llm_chain
        
    @staticmethod
    def index_document(doc_content: str, doc_id: int):
        """Index document text content."""
        try:
            embedding = create_embedding(doc_content)
            index.add(embedding.reshape(1, -1))  # Add embedding to the FAISS index
            documents[doc_id] = doc_content  # Store document content with ID
            logger.info(f"Indexed document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to index document {doc_id}: {e}\n{traceback.format_exc()}")
            raise e

    @staticmethod
    def query_document(query: str, threshold: float = 0.7) -> str:
        """Perform NLP-based query against indexed documents."""
        try:
            # Generate query embedding
            query_embedding = create_embedding(query).reshape(1, -1)
            
            # Retrieve relevant context using the query
            distances, indices = index.search(query_embedding, k=5)
            logger.info(f"Query: {query}")
            logger.info(f"Distances: {distances}, Indices: {indices}")

            # Filter out documents with distances above the threshold (low similarity)
            relevant_docs = [documents[idx] for dist, idx in zip(distances[0], indices[0]) if dist < threshold]
            
            if not relevant_docs:
                logger.warning("No relevant documents found within the similarity threshold.")
                return "No relevant documents found."

            # Prepare context from retrieved documents
            context = " ".join(relevant_docs)
            logger.info(f"Context for query '{query}': {context[:500]}...")  # Log a snippet of context

            # Check if LLMChain is properly initialized
            if llm_chain:
                response = llm_chain.run({"context": context, "query": query})
                logger.info("Response generated from QA chain.")
            else:
                response = "Simulated response based on context."
                logger.warning("LLMChain not properly initialized; using simulated response.")

            return response
        except Exception as e:
            logger.error(f"Query failed: {e}\n{traceback.format_exc()}")
            raise e
