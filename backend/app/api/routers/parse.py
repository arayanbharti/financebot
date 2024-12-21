from fastapi import APIRouter, HTTPException
from typing import Dict
from .services import parse_data
import os 


status_router= r = APIRouter()

# Initialize the parsing service
pdf_service = parse_data.PDFParsingService(
    pdf_api_key="llx-6j54eYNwS0br4hCj6sHOmRJhnBBEAMxIff6INts6GGP33pJS",
    llm_api_key="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",
    model="llama3-70b-8192",
)
from fastapi.responses import JSONResponse

@r.post("/start-parsing")
def start_parsing():
    """
    Start parsing the PDF.
    """
    try:
        uploads_dir = "./data/uploads"  # Replace with actual file path
        file_paths = [
            os.path.join(uploads_dir, file)
            for file in os.listdir(uploads_dir)
            if file.endswith(".pdf")
        ]

        # Check if there are any PDF files
        if not file_paths:
            return {"status": "error", "message": "No PDF files found in the upload directory."}

        output_file = "extracted_headings_and_tables.md"
        result = pdf_service.parse_pdf(file_paths, output_file)
        return {"status": "success", "details": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@r.get("/parsing-status")
async def parsing_status():
    """
    Check the parsing status.
    """
    status = pdf_service.is_parsing_complete()
    return {"parsing_complete": status}
   

@r.get("/html_graphs")
async def list_html_graphs():
    """
    List HTML graph files in the public/html_graphs directory.
    """
    try:
        print("Current Working Directory:", os.getcwd())
        print("Full path to graph dir:", os.path.abspath('public/html_graphs'))
        # Adjust the path as needed
        graph_dir = 'public/html_graphs'
        
        # Ensure the directory exists
        if not os.path.exists(graph_dir):
            raise HTTPException(status_code=404, detail="Graph directory not found")
        
        # List all files in the directory
        files = os.listdir(graph_dir)
        
        # Filter for HTML files
        html_files = [f for f in files if f.endswith('.html') or f.endswith('.htm')]
        
        return html_files
    except Exception as e:
        # Return a JSON response with error details
        return JSONResponse(
            status_code=500, 
            content={
                "error": str(e),
                "files": []
            }
        )