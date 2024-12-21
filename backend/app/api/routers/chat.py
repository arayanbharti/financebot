from typing import Any
from fastapi import APIRouter, HTTPException
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.llms.groq import Groq
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings


class ChatService:
    """
    A service for handling chat-based queries using Qdrant and LlamaIndex.
    """
    
    def __init__(self, qdrant_url: str, qdrant_api_key: str, collection_name: str, llm_model: str, embedding_model: str):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # Configure LlamaIndex settings
        Settings.embed_model = FastEmbedEmbedding(model_name=embedding_model)
        Settings.chunk_size = 1536
        Settings.llm = Groq(model=llm_model, api_key="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")
        
        # Load the index from Qdrant
        self.index = self._load_index_from_qdrant(collection_name)

    def _load_index_from_qdrant(self, collection_name: str) -> VectorStoreIndex:
        """
        Load the VectorStoreIndex from the Qdrant vector store.
        """
        vector_store = QdrantVectorStore(
            client=self.qdrant_client, collection_name=collection_name
        )
        return VectorStoreIndex.from_vector_store(vector_store=vector_store)

    def query(self, query_text: str):
        """
        Process the query using the VectorStoreIndex and return a response.
        """
        try:
            query_engine = self.index.as_query_engine()
            response = query_engine.query(query_text)
            return {"status": "success", "response": str(response)}
        except Exception as e:
            raise RuntimeError(f"Error processing query: {str(e)}")


# Initialize the chat service
chat_service = ChatService(
    qdrant_url="https://e95b74df-5314-4f6e-9889-950c89ec70e2.europe-west3-0.gcp.cloud.qdrant.io:6333",
    qdrant_api_key="X1TSj-E3gxXu52TNJbgA7YRIm_fPGTvSFgLNIiZNTvqcbYFILLuNuQ",
    collection_name="finance_agent_collection",
    llm_model="llama3-70b-8192",
    embedding_model="BAAI/bge-base-en-v1.5"
)


chat_router = r = APIRouter()

from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

@r.post("/chat")
async def query_agent(request: QueryRequest):
    """
    Handle chat requests and return the response from the query engine.
    """
    # try:
    result = chat_service.query(request.query)
    print("query response: %s", result)
    return result
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")
