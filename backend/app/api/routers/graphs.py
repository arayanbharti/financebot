
from fastapi import APIRouter, HTTPException
from typing import Dict
from .services import parse_data
import os 
import json


status_router= r = APIRouter()


@app.route('/html_graphs', methods=['GET'])
def list_html_graphs():
    import os
    
    # Adjust the path as needed
    graph_dir = 'public/html_graphs'
    
    try:
        # List all files in the directory
        files = os.listdir(graph_dir)
        
        # Filter for HTML files
        html_files = [f for f in files if f.endswith('.html') or f.endswith('.htm')]
        
        return json.loads(html_files)
    except Exception as e:
        return json.loads({'error': str(e)}), 500