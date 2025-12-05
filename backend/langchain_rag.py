"""
LangChain RAG Application - Using Vertex AI RAG Engine and Fine-tuned Model

This application implements RAG workflow using LangChain framework:
1. Custom Retriever - Using Vertex AI Managed RAG Engine
2. Custom LLM - Using Fine-tuned Model Endpoint
3. LCEL Chain - Using LangChain Expression Language for orchestration
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import vertexai
from google.cloud import aiplatform

# Try to load .env file
try:
    from dotenv import load_dotenv
    # Try to load from backend/.env or root .env
    env_paths = [
        Path(__file__).parent / ".env",  # backend/.env
        Path(__file__).parent.parent / ".env",  # root .env
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            logger = logging.getLogger(__name__)
            logger.info(f"Loaded .env file: {env_path}")
            break
except ImportError:
    # If python-dotenv is not available, try manual parsing
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            break

# LangChain imports
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from pydantic import Field, PrivateAttr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration Variables
# ============================================================================

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "europe-north1")
RAG_CORPUS_ID = os.getenv("RAG_CORPUS_ID", "gems-corpus")
FINE_TUNED_ENDPOINT_ID = os.getenv("FINE_TUNED_ENDPOINT_ID", "")
FINE_TUNED_MODEL_ID = os.getenv("FINE_TUNED_MODEL_ID", "")  # Fine-tuned Model ID (use model ID directly)

# Initialize Vertex AI
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    logger.info(f"Vertex AI initialized successfully: project={PROJECT_ID}, location={LOCATION}")
except Exception as e:
    logger.error(f"Vertex AI initialization failed: {e}")
    raise


# ============================================================================
# 1. Custom Retriever - Vertex AI RAG Engine
# ============================================================================

class VertexRAGEngineRetriever(BaseRetriever):
    """
    Custom retriever using Vertex AI Managed RAG Engine
    
    Inherits from LangChain's BaseRetriever, implements _get_relevant_documents method
    Uses vertexai.preview.rag.retrieval_query to retrieve documents from RAG Corpus
    """
    
    project_id: str = Field(default=PROJECT_ID, description="Google Cloud Project ID")
    location: str = Field(default=LOCATION, description="Vertex AI Region")
    rag_corpus_id: str = Field(default=RAG_CORPUS_ID, description="RAG Corpus ID")
    top_k: int = Field(default=5, description="Number of documents to return")
    corpus_name: str = Field(default="", description="Full Corpus resource name")
    
    def model_post_init(self, __context: Any) -> None:
        """Build full Corpus resource name after model initialization"""
        if not self.corpus_name:
            self.corpus_name = f"projects/{self.project_id}/locations/{self.location}/ragCorpora/{self.rag_corpus_id}"
        logger.info(f"Initialized VertexRAGEngineRetriever: corpus={self.corpus_name}")
    
    def _get_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: Optional[Any] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents from Vertex AI RAG Engine
        
        Args:
            query: User query text
            run_manager: LangChain run manager (optional)
            
        Returns:
            List of Document objects
        """
        try:
            from vertexai.preview import rag
            
            logger.info(f"Retrieval query: '{query[:50]}...' (top_k={self.top_k})")
            
            # Execute RAG retrieval query
            response = rag.retrieval_query(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=self.corpus_name,
                    )
                ],
                text=query,
                rag_retrieval_config=rag.RagRetrievalConfig(
                    top_k=self.top_k,
                    # Use hybrid search to improve retrieval quality
                    hybrid_search=rag.HybridSearch(
                        alpha=0.5  # Balance between dense and sparse vector search
                    ),
                ),
            )
            
            # Extract retrieved contexts and convert to LangChain Document objects
            documents = []
            
            if hasattr(response, 'contexts'):
                rag_contexts = response.contexts
                
                # RagContexts has a 'contexts' attribute which is a list
                if hasattr(rag_contexts, 'contexts') and rag_contexts.contexts:
                    for context in rag_contexts.contexts:
                        # Each context has 'text' and optionally 'source_uri'
                        if hasattr(context, 'text') and context.text:
                            # Create LangChain Document object
                            metadata = {}
                            if hasattr(context, 'source_uri') and context.source_uri:
                                metadata['source'] = context.source_uri
                            
                            doc = Document(
                                page_content=context.text,
                                metadata=metadata
                            )
                            documents.append(doc)
                
                # Fallback: if contexts is directly accessible
                elif isinstance(rag_contexts, (list, tuple)):
                    for context in rag_contexts:
                        if hasattr(context, 'text') and context.text:
                            metadata = {}
                            if hasattr(context, 'source_uri') and context.source_uri:
                                metadata['source'] = context.source_uri
                            
                            doc = Document(
                                page_content=context.text,
                                metadata=metadata
                            )
                            documents.append(doc)
                        elif isinstance(context, str):
                            doc = Document(page_content=context)
                            documents.append(doc)
            
            logger.info(f"Retrieval completed: found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _aget_relevant_documents(
        self, 
        query: str, 
        *, 
        run_manager: Optional[Any] = None
    ) -> List[Document]:
        """
        Async version of retrieval method (optional implementation)
        """
        # Since vertexai.preview.rag may not support async, call sync version here
        return self._get_relevant_documents(query, run_manager=run_manager)


# ============================================================================
# 2. Custom LLM - Fine-tuned Model Endpoint
# ============================================================================

class VertexCustomEndpoint(LLM):
    """
    Custom LLM using Vertex AI Fine-tuned Gemini Model
    
    Inherits from LangChain's LLM base class, implements _call method
    Note: Fine-tuned Gemini models need to use GenerativeModel, not Endpoint API
    """
    
    project_id: str = Field(default=PROJECT_ID, description="Google Cloud Project ID")
    location: str = Field(default=LOCATION, description="Vertex AI Region")
    model_id: str = Field(default="", description="Fine-tuned Model ID (obtained from Endpoint)")
    temperature: float = Field(default=0.2, description="Generation temperature")
    top_p: float = Field(default=0.95, description="Top-p sampling parameter")
    top_k: int = Field(default=40, description="Top-k sampling parameter")
    max_output_tokens: int = Field(default=2048, description="Maximum output tokens")
    
    _model: Any = PrivateAttr(default=None)
    
    def model_post_init(self, __context: Any) -> None:
        """Process model ID after model initialization"""
        # If model_id is not provided, try to get from environment variables
        if not self.model_id or self.model_id == "":
            # Prefer FINE_TUNED_MODEL_ID (direct model ID)
            model_id = os.getenv("FINE_TUNED_MODEL_ID", "")
            if model_id:
                # Build full path
                self.model_id = f"projects/{self.project_id}/locations/{self.location}/models/{model_id}"
                logger.info(f"Using model ID from environment variable: {self.model_id}")
            else:
                # If no direct model ID, try to get from Endpoint
                endpoint_id = os.getenv("FINE_TUNED_ENDPOINT_ID", "")
                if endpoint_id:
                    self._endpoint_id_for_lookup = endpoint_id
                    logger.info(f"Will use Endpoint ID {endpoint_id} to find model")
                else:
                    raise ValueError("model_id must be set, or provide FINE_TUNED_MODEL_ID or FINE_TUNED_ENDPOINT_ID environment variable")
        else:
            self._endpoint_id_for_lookup = None
            logger.info(f"Initialized VertexCustomEndpoint: model={self.model_id}")
    
    @property
    def model(self):
        """Lazy initialization of GenerativeModel"""
        if self._model is None:
            from vertexai.generative_models import GenerativeModel
            
            # If model_id is not available yet, try to get from Endpoint
            if not self.model_id or self.model_id == "":
                if hasattr(self, '_endpoint_id_for_lookup') and self._endpoint_id_for_lookup:
                    try:
                        from google.cloud import aiplatform
                        endpoint_name = f"projects/{self.project_id}/locations/{self.location}/endpoints/{self._endpoint_id_for_lookup}"
                        endpoint = aiplatform.Endpoint(endpoint_name)
                        # Get deployed model
                        if hasattr(endpoint, 'deployed_models') and endpoint.deployed_models:
                            deployed_model = endpoint.deployed_models[0]
                            # Extract model path (format: projects/.../locations/.../models/MODEL_ID)
                            if hasattr(deployed_model, 'model'):
                                model_path = deployed_model.model
                                # Use full path as model ID
                                self.model_id = model_path
                                logger.info(f"Retrieved model path from Endpoint: {self.model_id}")
                    except Exception as e:
                        logger.error(f"Failed to get model from Endpoint: {e}")
                        raise ValueError(f"Failed to get model information from Endpoint {self._endpoint_id_for_lookup}: {e}")
                else:
                    raise ValueError("model_id must be set")
            
            # Create GenerativeModel
            self._model = GenerativeModel(self.model_id)
            logger.info(f"Created GenerativeModel: {self.model_id}")
        return self._model
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type identifier"""
        return "vertex_custom_endpoint"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call Fine-tuned Model Endpoint to generate response
        
        Args:
            prompt: Input prompt text
            stop: Stop words list (optional)
            run_manager: LangChain run manager (optional)
            **kwargs: Other parameters
            
        Returns:
            Generated text
        """
        try:
            logger.info(f"Calling Fine-tuned Gemini Model: prompt_length={len(prompt)}")
            
            # Use GenerativeModel to call Fine-tuned Gemini model
            generation_config = {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "max_output_tokens": self.max_output_tokens,
            }
            
            # Call model to generate
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract generated text
            if hasattr(response, 'text') and response.text:
                logger.info("Successfully generated response")
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Try to extract from candidates
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            logger.info("Successfully generated response (from candidates)")
                            return part.text
            
            raise ValueError("Model returned empty response")
            
        except Exception as e:
            logger.error(f"Error calling Fine-tuned Model Endpoint: {e}")
            import traceback
            traceback.print_exc()
            raise


# ============================================================================
# 3. LangChain Chain - Using LCEL
# ============================================================================

def create_rag_chain(
    retriever: Optional[VertexRAGEngineRetriever] = None,
    llm: Optional[VertexCustomEndpoint] = None,
    prompt_template: Optional[str] = None
):
    """
    Create RAG Chain using LangChain Expression Language (LCEL)
    
    Args:
        retriever: Custom retriever (optional, creates new one by default)
        llm: Custom LLM (optional, creates new one by default)
        prompt_template: Prompt template (optional, uses default template)
        
    Returns:
        LangChain Chain
    """
    # Create retriever (if not provided)
    if retriever is None:
        retriever = VertexRAGEngineRetriever(
            project_id=PROJECT_ID,
            location=LOCATION,
            rag_corpus_id=RAG_CORPUS_ID,
            top_k=5
        )
    
    # Create LLM (if not provided)
    if llm is None:
        if not FINE_TUNED_ENDPOINT_ID or FINE_TUNED_ENDPOINT_ID == "":
            raise ValueError("FINE_TUNED_ENDPOINT_ID must be set")
        
        llm = VertexCustomEndpoint(
            project_id=PROJECT_ID,
            location=LOCATION,
            endpoint_id=FINE_TUNED_ENDPOINT_ID,
            temperature=0.2,
            max_output_tokens=2048
        )
    
    # Default Prompt template
    if prompt_template is None:
        prompt_template = """Please answer the question based on the following retrieved document content. If there is no relevant information in the documents, please state so clearly.

Retrieved document content:
{context}

User question: {question}

Please answer the question STRICTLY based on the document content above. If there is no relevant information in the documents, please clearly state "Based on the retrieved documents, I cannot find relevant information to answer this question."

Answer:"""
    
    # Create Prompt template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Build LCEL Chain
    # Structure: {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    chain = (
        {
            "context": retriever,  # Retriever gets context
            "question": RunnablePassthrough()  # Pass user question directly
        }
        | prompt  # Format Prompt
        | llm  # Call LLM to generate answer
        | StrOutputParser()  # Parse output as string
    )
    
    logger.info("RAG Chain created successfully")
    return chain


# ============================================================================
# 4. Main Function - Usage Example
# ============================================================================

def main():
    """
    Main function: Demonstrates how to use LangChain RAG Chain
    """
    print("\n" + "=" * 60)
    print("LangChain RAG Application - Vertex AI + Fine-tuned Model")
    print("=" * 60)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Region: {LOCATION}")
    print(f"RAG Corpus ID: {RAG_CORPUS_ID}")
    print(f"Endpoint ID: {FINE_TUNED_ENDPOINT_ID}")
    print("=" * 60 + "\n")
    
    try:
        # Create RAG Chain
        chain = create_rag_chain()
        
        # Example queries
        example_queries = [
            "What is GEMS Agent?",
            "Please introduce the company's resource management process",
        ]
        
        print("Please enter your question (type 'quit' to exit):")
        
        while True:
            try:
                user_query = input("\n> ").strip()
                
                if not user_query:
                    continue
                
                if user_query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                # Invoke Chain (LangChain will automatically handle retrieval and generation)
                print("\nProcessing...")
                answer = chain.invoke(user_query)
                
                print("\n" + "-" * 60)
                print("Answer:")
                print("-" * 60)
                print(answer)
                print("-" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nProgram interrupted by user.")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                import traceback
                traceback.print_exc()
                print(f"\nError occurred: {e}\n")
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nInitialization failed: {e}")
        print("\nPlease check:")
        print("1. Are environment variables set correctly?")
        print("2. Is FINE_TUNED_ENDPOINT_ID configured?")
        print("3. Are Vertex AI permissions correct?")


if __name__ == "__main__":
    main()

