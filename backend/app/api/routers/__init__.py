from fastapi import APIRouter

# from .papers import paper_router
# from .report import report_router
from .uploads import upload_router
from .parse import status_router
from .chat import chat_router

api_router = APIRouter()
api_router.include_router(upload_router, prefix="/uploads")
api_router.include_router(status_router, prefix="/parse")
api_router.include_router(chat_router, prefix="/agent")