"""
GEMS Agent API - Backend service for calling Vertex AI RAG Engine
Also serves frontend static files when deployed to Cloud Run
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import vertexai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title="GEMS Agent API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "europe-west1")  # Updated to europe-west1 for new corpus
RAG_CORPUS_ID = os.getenv("RAG_CORPUS_ID", "your-rag-corpus-id")

# System instruction for the AI Agent
SYSTEM_INSTRUCTION = os.getenv(
    "SYSTEM_INSTRUCTION",
    """You are an AI Agent built for a consulting company to support resource management, sales enablement, market analysis, and operational automation.

Your primary purpose is to transform siloed company data (Recman, Flowcase/CVpartner, Gmail, internal docs) into actionable insights and assist users in making better decisions faster."""
)

# Initialize Vertex AI
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    print(f"Warning: Vertex AI initialization failed: {e}")
    print("Make sure GOOGLE_CLOUD_PROJECT and VERTEX_AI_LOCATION are set correctly")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def is_about_agent_itself(query: str) -> bool:
    """
    Check if the question is about GEMS Agent itself (not company data).
    If so, answer directly based on System Instruction without RAG retrieval.
    """
    query_lower = query.lower().strip()
    agent_keywords = [
        # English keywords
        "what is this", "what is gems", "what are you", "who are you",
        "what can you do", "what do you do", "what is your purpose",
        "what is your role", "what is your function", "what are you for",
        "tell me about yourself", "describe yourself", "introduce yourself",
        # Norwegian keywords
        "hva er dette", "hva er gems", "hva er du", "hvem er du",
        "hva kan du gjøre", "hva gjør du", "hva er ditt formål",
        "hva er din rolle", "hva er din funksjon", "fortell om deg selv",
        "beskriv deg selv", "introduser deg selv"
    ]
    return any(keyword in query_lower for keyword in agent_keywords)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "GEMS Agent API",
        "project": PROJECT_ID,
        "location": LOCATION,
        "rag_corpus_id": RAG_CORPUS_ID,
        "system_instruction_configured": bool(SYSTEM_INSTRUCTION),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that calls Vertex AI RAG Engine
    
    Args:
        request: ChatRequest with user message
        
    Returns:
        ChatResponse with RAG search results
    """
    import logging
    import time
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    
    # Log request
    request_time = datetime.now().isoformat()
    message_text = request.message.strip() if request.message else ""
    
    logger.info(f"[{request_time}] Received chat request: message_length={len(message_text)}")
    print(f"[{request_time}] [INFO] Received chat request: message='{message_text[:50]}...' (length: {len(message_text)})")
    
    if not request.message or not request.message.strip():
        logger.warning(f"[{request_time}] Empty message request")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        start_time = time.time()
        # Using Vertex AI RAG Engine via vertexai.preview.rag module
        try:
            from vertexai.preview import rag
        except ImportError:
            try:
                from vertexai import rag
            except ImportError:
                # Try alternative import
                import vertexai.preview.rag as rag
        
        # Note: vertexai is already initialized at module level (line 31)
        
        # Execute retrieval query
        query_text = request.message.strip()
        
        # Check if question is about GEMS Agent itself (not company data)
        # If so, answer directly based on System Instruction, skip RAG retrieval
        if is_about_agent_itself(query_text):
            logger.info(f"[{request_time}] Detected question about Agent itself, skipping RAG retrieval")
            print(f"[{request_time}] [INFO] Question about Agent itself, answering based on System Instruction")
            
            # Detect language
            query_lower = query_text.lower()
            is_english = any(word in query_lower for word in [
                'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'can', 'will',
                'the', 'a', 'an', 'and', 'or', 'but', 'hello', 'hi', 'please', 'thank',
                'tell', 'describe', 'introduce'
            ])
            is_norwegian = any(word in query_lower for word in [
                'hva', 'hvem', 'hvor', 'når', 'hvorfor', 'hvordan', 'er', 'kan', 'vil',
                'og', 'eller', 'men', 'hei', 'hallo', 'takk', 'vær', 'snill',
                'fortell', 'beskriv', 'introduser'
            ])
            
            if is_english and not is_norwegian:
                response_language = "English"
                language_instruction = "Please respond in English."
            else:
                response_language = "Norwegian"
                language_instruction = "Vennligst svar på norsk."
            
            # Use Gemini to generate answer based on System Instruction only
            from vertexai.generative_models import GenerativeModel
            
            # Try models available in europe-west1 region
            model_priority = [
                os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
                "gemini-2.5-pro",
                "gemini-2.0-pro",
                "gemini-1.5-pro",
                "gemini-pro",
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            model_priority = [m for m in model_priority if not (m in seen or seen.add(m))]
            
            model = None
            model_name_used = None
            
            # Try to find an available model
            for model_name in model_priority:
                try:
                    model = GenerativeModel(model_name, system_instruction=SYSTEM_INSTRUCTION)
                    # Test if model can actually generate
                    test_response = model.generate_content("test", generation_config={"max_output_tokens": 5})
                    model_name_used = model_name
                    logger.info(f"[{request_time}] Using model: {model_name} for Agent self-question")
                    break
                except Exception as model_error:
                    logger.debug(f"[{request_time}] Model {model_name} not available: {str(model_error)[:100]}")
                    model = None
                    continue
            
            if model is not None:
                # Create simple prompt that relies on System Instruction
                if response_language == "English":
                    prompt = f"""User question: {query_text}

{language_instruction}"""
                else:
                    prompt = f"""Brukerens spørsmål: {query_text}

{language_instruction}"""
                
                generation_config = {
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
                
                try:
                    generated_response = model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    reply = generated_response.text if hasattr(generated_response, 'text') else str(generated_response)
                    
                    if not reply or not reply.strip():
                        # Fallback to default answer
                        if response_language == "English":
                            reply = "I am GEMS Agent, an AI assistant for resource management, sales enablement, market analysis, and operational automation. I help transform company data into actionable insights."
                        else:
                            reply = "Jeg er GEMS Agent, en AI-assistent for ressursforvaltning, salgsstøtte, markedanalyse og operasjonsautomatisering. Jeg hjelper til med å transformere selskapsdata til handlingsrettede innsikter."
                    
                    elapsed_time = time.time() - start_time
                    logger.info(f"[{request_time}] Agent self-question answered: reply_length={len(reply)}, duration={elapsed_time:.2f}s")
                    print(f"[{request_time}] [SUCCESS] Agent self-question answered: reply length {len(reply)} chars, duration {elapsed_time:.2f}s")
                    
                    return ChatResponse(reply=reply)
                except Exception as gen_error:
                    logger.warning(f"[{request_time}] Generation error for Agent self-question: {str(gen_error)[:150]}")
                    # Fallback to default answer
                    if response_language == "English":
                        reply = "I am GEMS Agent, an AI assistant for resource management, sales enablement, market analysis, and operational automation."
                    else:
                        reply = "Jeg er GEMS Agent, en AI-assistent for ressursforvaltning, salgsstøtte, markedanalyse og operasjonsautomatisering."
                    
                    elapsed_time = time.time() - start_time
                    return ChatResponse(reply=reply)
            else:
                # No model available, return default answer
                if response_language == "English":
                    reply = "I am GEMS Agent, an AI assistant for resource management, sales enablement, market analysis, and operational automation."
                else:
                    reply = "Jeg er GEMS Agent, en AI-assistent for ressursforvaltning, salgsstøtte, markedanalyse og operasjonsautomatisering."
                
                elapsed_time = time.time() - start_time
                logger.warning(f"[{request_time}] No model available for Agent self-question, using default answer")
                return ChatResponse(reply=reply)
        
        # If question is about company data, proceed with RAG retrieval
        # Prepare the corpus resource name
        corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{RAG_CORPUS_ID}"
        
        # Enhanced RAG retrieval configuration with LLM Ranker and Hybrid Search
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name,
                )
            ],
            text=query_text,
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=10,  # Retrieve more results for better context
                # Note: LLM Ranker may not be available in all regions
                # Using hybrid_search for better retrieval quality
                hybrid_search=rag.HybridSearch(
                    alpha=0.5  # Balance between dense and sparse vector search
                ),
            ),
        )
        
        # Extract contexts from response
        # Response structure: RetrieveContextsResponse -> contexts (RagContexts) -> contexts (list of Context)
        contexts = []
        
        if hasattr(response, 'contexts'):
            rag_contexts = response.contexts
            
            # RagContexts has a 'contexts' attribute which is a list
            if hasattr(rag_contexts, 'contexts') and rag_contexts.contexts:
                for context in rag_contexts.contexts:
                    # Each context has 'text' and optionally 'source_uri'
                    if hasattr(context, 'text') and context.text:
                        contexts.append(context.text)
                    elif hasattr(context, 'source_uri') and context.source_uri:
                        contexts.append(f"Source: {context.source_uri}")
            
            # Fallback: if contexts is directly accessible
            elif isinstance(rag_contexts, (list, tuple)):
                for context in rag_contexts:
                    if hasattr(context, 'text') and context.text:
                        contexts.append(context.text)
                    elif isinstance(context, str):
                        contexts.append(context)
        
        # Generate answer using Gemini model based on retrieved contexts
        if contexts:
            # Combine contexts into a single prompt
            context_text = "\n\n".join(contexts[:5])  # Use top 5 contexts
            
            # Detect language of user's question
            # Simple language detection based on common words/patterns
            query_lower = query_text.lower()
            is_english = any(word in query_lower for word in [
                'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'can', 'will',
                'the', 'a', 'an', 'and', 'or', 'but', 'hello', 'hi', 'please', 'thank'
            ])
            is_norwegian = any(word in query_lower for word in [
                'hva', 'hvem', 'hvor', 'når', 'hvorfor', 'hvordan', 'er', 'kan', 'vil',
                'og', 'eller', 'men', 'hei', 'hallo', 'takk', 'vær', 'snill'
            ])
            
            # Determine response language (default to Norwegian if unclear)
            if is_english and not is_norwegian:
                response_language = "English"
                language_instruction = "Please respond in English."
            elif is_norwegian or (not is_english and not is_norwegian):
                response_language = "Norwegian"
                language_instruction = "Vennligst svar på norsk."
            else:
                # If both detected, prefer Norwegian
                response_language = "Norwegian"
                language_instruction = "Vennligst svar på norsk."
            
            logger.info(f"[{request_time}] Detected language: {response_language} for query: '{query_text[:50]}...'")
            
            # Use Gemini to generate a natural language answer
            # Note: All operations must use the same region (europe-west1) as RAG Corpus
            from vertexai.generative_models import GenerativeModel
            
            # Try models available in europe-west1 region
            # europe-west1 typically has better model availability than europe-north1
            # Only use Pro models, no Flash models (as Flash produces poor quality results)
            model_priority = [
                os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),  # Use env var or default to gemini-2.5-pro
                "gemini-2.5-pro",  # Latest 2.5 pro model
                "gemini-2.0-pro",  # 2.0 pro model
                "gemini-1.5-pro",  # Stable 1.5 pro model
                "gemini-pro",  # First generation pro model as fallback
            ]
            
            # Remove duplicates while preserving order
            seen = set()
            model_priority = [m for m in model_priority if not (m in seen or seen.add(m))]
            
            model = None
            model_name_used = None
            
            # Try to find an available model in europe-west1
            for model_name in model_priority:
                try:
                    model = GenerativeModel(model_name, system_instruction=SYSTEM_INSTRUCTION)
                    # Test if model can actually generate
                    test_response = model.generate_content("test", generation_config={"max_output_tokens": 5})
                    model_name_used = model_name
                    logger.info(f"[{request_time}] Using model: {model_name} in {LOCATION}")
                    break
                except Exception as model_error:
                    error_msg = str(model_error)
                    logger.debug(f"[{request_time}] Model {model_name} not available in {LOCATION}: {error_msg[:100]}")
                    model = None
                    continue
            
            # Only generate if model is available
            if model is not None:
                # Create language-appropriate prompt with better context relevance handling
                if response_language == "English":
                    prompt = f"""User question: {query_text}

Retrieved information from knowledge base:
{context_text}

Instructions:
- If the retrieved information is relevant to the question, use it to provide a comprehensive answer.
- If the retrieved information is not relevant to the question, clearly state that and answer based on your role as GEMS Agent (as defined in your system instructions).
- {language_instruction}
- Be professional and precise."""
                else:  # Norwegian
                    prompt = f"""Brukerens spørsmål: {query_text}

Hentet informasjon fra kunnskapsbasen:
{context_text}

Instruksjoner:
- Hvis den hentede informasjonen er relevant for spørsmålet, bruk den til å gi et omfattende svar.
- Hvis den hentede informasjonen ikke er relevant for spørsmålet, si det tydelig og svar basert på din rolle som GEMS Agent (som definert i systeminstruksjonene dine).
- {language_instruction}
- Vær profesjonell og presis."""
                
                generation_config = {
                    "temperature": 0.2,  # Lower temperature for more focused, professional answers
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
                
                try:
                    generated_response = model.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    
                    reply = generated_response.text if hasattr(generated_response, 'text') else str(generated_response)
                    
                    if not reply or not reply.strip():
                        # Fallback to raw contexts if generation fails
                        reply = "\n\n---\n\n".join(contexts)
                        logger.warning(f"[{request_time}] Gemini generation returned empty, using raw contexts")
                    else:
                        logger.info(f"[{request_time}] Successfully generated answer using {model_name_used}")
                except Exception as gen_error:
                    # Fallback to raw contexts if generation fails
                    logger.warning(f"[{request_time}] Gemini generation error: {str(gen_error)[:150]}, using raw contexts")
                    reply = "\n\n---\n\n".join(contexts)
            else:
                # No model available, return raw contexts with a note
                logger.warning(f"[{request_time}] No Gemini generation model available in {LOCATION}, returning raw RAG contexts")
            reply = "\n\n---\n\n".join(contexts)
        else:
            # Detect language for error message
            query_lower = query_text.lower()
            is_english = any(word in query_lower for word in [
                'what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'can', 'will',
                'the', 'a', 'an', 'and', 'or', 'but', 'hello', 'hi', 'please', 'thank'
            ])
            
            if is_english:
                reply = "Sorry, I could not find relevant information in the knowledge base to answer your question."
            else:
                reply = "Beklager, jeg fant ikke relevant informasjon i kunnskapsbasen for å svare på spørsmålet ditt."
        
        elapsed_time = time.time() - start_time
        logger.info(f"[{request_time}] Request successful: contexts_count={len(contexts)}, reply_length={len(reply)}, duration={elapsed_time:.2f}s")
        print(f"[{request_time}] [SUCCESS] Request completed: returned {len(contexts)} contexts, reply length {len(reply)} chars, duration {elapsed_time:.2f}s")
        
        return ChatResponse(reply=reply)
        
    except Exception as e:
        elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
        error_detail = f"Failed to get response from RAG Engine: {str(e)}"
        
        logger.error(f"[{request_time}] Request failed: error={error_detail}, duration={elapsed_time:.2f}s")
        print(f"[{request_time}] [ERROR] Request failed: {error_detail}")
        print(f"[{request_time}] [ERROR] PROJECT_ID={PROJECT_ID}, LOCATION={LOCATION}, RAG_CORPUS_ID={RAG_CORPUS_ID}")
        print(f"[{request_time}] [ERROR] Duration: {elapsed_time:.2f}s")
        
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Serve frontend static files (for Cloud Run deployment)
# This allows the backend to serve both API and frontend from the same service
frontend_dist = Path(__file__).parent.parent / "dist"

if frontend_dist.exists():
    # Serve static assets (JS, CSS, images)
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    # Serve other static files (like images in public folder)
    @app.get("/{filename:path}")
    async def serve_frontend(filename: str):
        """
        Serve frontend files. 
        API routes are handled above, so this only catches non-API requests.
        """
        # Skip API routes
        if filename in ("chat", "health") or filename.startswith("api/"):
            raise HTTPException(status_code=404)
        
        file_path = frontend_dist / filename
        
        # Check if path is within frontend_dist (security check)
        try:
            file_path.resolve().relative_to(frontend_dist.resolve())
        except ValueError:
            # Path is outside frontend_dist, serve index.html instead
            filename = "index.html"
            file_path = frontend_dist / filename
        
        # If file exists, serve it
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Otherwise serve index.html (for React Router or direct file access)
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

