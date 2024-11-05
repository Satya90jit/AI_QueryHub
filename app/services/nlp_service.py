from sentence_transformers import SentenceTransformer
import faiss
from app.schemas.document import DocumentOut  # Ensure this schema exists
import logging
import traceback  # For better error handling
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import create_retrieval_chain

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
    def query_document(query: str) -> str:
        """Perform NLP-based query against indexed documents."""
        try:
            # Generate query embedding
            query_embedding = create_embedding(query).reshape(1, -1)
            
            # Retrieve relevant context using the query
            distances, indices = index.search(query_embedding, k=5)  # Retrieve top 5 similar docs
            logger.info(f"Query: {query}")
            logger.info(f"Documents found: {len(indices[0])}")

            if indices[0][0] == -1:  # Check if no relevant documents were found
                logger.warning("No relevant documents found.")
                return "No relevant documents found."

            # Prepare context from retrieved documents
            relevant_docs = [documents[idx] for idx in indices[0] if idx != -1]
            context = " ".join(relevant_docs)
            logger.info("Context prepared for the query.")

            # Create a simple prompt template for question generation
            question_prompt_template = PromptTemplate(
                template="Generate a response based on this context: {context}",
                input_variables=["context"]
            )
            
            # Initialize LLMChain with the context (you might use a local LLM or generate text here)
            llm_chain = LLMChain(llm=None, prompt=question_prompt_template)  # Replace None with your own LLM if available
            
            inputs = {
                "context": context,
                "query": query
            }
            response = llm_chain.run(inputs) if llm_chain else "Simulated response based on context."
            logger.info("Response generated from QA chain.")
            return response
        except Exception as e:
            logger.error(f"Query failed: {e}\n{traceback.format_exc()}")
            raise e
