import os
import base64
import shutil
import logging
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

upload_router = r = APIRouter()

logger = logging.getLogger("uvicorn")


class PDFUploadRequest(BaseModel):
    files: List[str] = Field(..., description="List of Base64-encoded PDF files.")
    # pass


def empty_directory(directory_path: str):
    """
    Empty the given directory and recreate it if it doesn't exist.
    """
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        os.makedirs(directory_path)
    except Exception as e:
        logger.error(f"Error while emptying directory: {directory_path}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clean directory: {directory_path}")


@r.post("/finance-data")
async def upload_files(request: PDFUploadRequest):
    """
    Endpoint to handle Base64-encoded PDF uploads.
    """
    directory_path = "./data/uploads"
    empty_directory(directory_path)  # Clear directory first
    empty_directory("./public/html_graphs")

    saved_files = []
    try:
        for idx, encoded_file in enumerate(request.files):
            try:
                file_data = base64.b64decode(encoded_file)
                file_path = os.path.join(directory_path, f"file_{idx + 1}.pdf")
                with open(file_path, "wb") as f:
                    f.write(file_data)
                saved_files.append(file_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decode and save file {idx + 1}: {str(e)}")

        return {"message": "Files uploaded successfully.", "saved_files": saved_files}

    except Exception as e:
        logger.error(f"Error while processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload files. Error: {str(e)}")
