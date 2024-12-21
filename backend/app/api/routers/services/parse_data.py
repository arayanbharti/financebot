import os
import re
import logging
from typing import List, Dict, Optional

import qdrant_client
from llama_parse import LlamaParse
from llama_index.llms.groq import Groq
from llama_index.core.llms import ChatMessage
from llama_index.core import (
    VectorStoreIndex, 
    StorageContext, 
    Settings, 
    Document
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from qdrant_client.http import models as rest

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFParsingService:
    """
    A comprehensive service for parsing PDFs, extracting tables, 
    generating summaries, and indexing in a vector database.
    """
    def __init__(
        self, 
        pdf_api_key: str, 
        llm_api_key: str, 
        model: str = "mixtral-8x7b-32768", 
        output_dir: str = "./public"
    ):
        """
        Initialize the PDF parsing service.

        Args:
            pdf_api_key (str): API key for PDF parsing service
            llm_api_key (str): API key for language model
            model (str, optional): LLM model to use. Defaults to Groq's Mixtral.
            output_dir (str, optional): Directory to save output files. Defaults to "./public".
        """
        try:
            # Configure embedding and chunking
            Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")
            Settings.chunk_size = 1536

            # Initialize PDF parser and LLM
            self.pdf_parser = LlamaParse(
                api_key=pdf_api_key, 
                result_type="markdown", 
                verbose=True
            )
            self.llm = Groq(model=model, api_key=llm_api_key)
            
            # Setup Qdrant client and vector store
            self.qdrant_client = qdrant_client.QdrantClient(
                url="https://e95b74df-5314-4f6e-9889-950c89ec70e2.europe-west3-0.gcp.cloud.qdrant.io:6333",
                api_key="X1TSj-E3gxXu52TNJbgA7YRIm_fPGTvSFgLNIiZNTvqcbYFILLuNuQ"
            )
            self.vector_store = QdrantVectorStore(
                client=self.qdrant_client, 
                collection_name="finance_agent_collection"
            )

            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.parsing_status = False
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise

    def clean_html_code(self, raw_html: str) -> str:
        """
        Cleans and formats the extracted HTML code by removing unnecessary escape sequences and extra whitespace.

        Args:
            raw_html (str): Raw HTML string with noise (e.g., `\n`, `\\`).

        Returns:
            str: Cleaned and properly formatted HTML code.
        """
        try:
            # Remove unwanted escape characters like `\n`
            cleaned_html = raw_html.replace("\n","")

            # Remove any leading or trailing whitespace
            # cleaned_html = cleaned_html.strip()

            # Ensure proper formatting by removing excessive empty lines
            # cleaned_html = re.sub(r"\n\s*\n", "\n", cleaned_html)

            return cleaned_html
        except Exception as e:
            print(f"Error during HTML cleaning: {e}")
            return raw_html


    def extract_html_code(self, index_name, llm_response: str) -> str:
        """
        Extract HTML code dynamically from the LLM response.

        Args:
            llm_response (str): The response from the LLM containing the HTML code.

        Returns:
            str: Extracted HTML code, or an empty string if no code block is found.
        """
        try:
            # Regular expression to extract content between ```html and ```
            html_pattern = r"```html\n(.*?)```"
            match = re.search(html_pattern, llm_response, re.DOTALL)
            if match:
                html_code = match.group(1).strip()
                # html_code = self.clean_html_code(html_code)
                # Specify the file name
                output_file = f"public/html_graphs/{index_name}.html"

                # Write the HTML code to the file
                static_head = """
                                <head>
                                    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                                    <script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.20.0/plotly.min.js"></script>
                                </head>
                                """
                complete_html = static_head + html_code
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(complete_html)
                return complete_html
            else:
                print("No HTML code block found in the response.")
                return ""
        except Exception as e:
            print(f"Error extracting HTML code: {e}")
            return ""
        
    def _extract_headings_and_tables(self, documents: List[Document]) -> List[str]:
        """
        Extract headings and corresponding tables from markdown documents.

        Args:
            documents (List[Document]): Parsed markdown documents

        Returns:
            List[str]: Extracted tables with their headings
        """
        extracted = []
        pattern = r"(#+ .*\n+)(\|.*?\|\n(?:\|[-:]+[-| :]*\|\n)+(?:\|.*?\|\n)+)"

        for doc in documents:
            matches = re.findall(pattern, doc.text, re.MULTILINE | re.DOTALL)
            extracted.extend([f"\n\n{heading.strip()}\n\n{table.strip()}\n\n" 
                              for heading, table in matches])

        return extracted

    def _summarize_table(self, markdown_table: str) -> str:
        """
        Generate a summary of a markdown table using LLM.

        Args:
            markdown_table (str): Markdown formatted table

        Returns:
            str: Summarized content of the table
        """
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="Summarize the financial data of a company provided in the markdown table. "
                            "Write a summary that captures all key insights, including revenue, "
                            "expenses, profits, and trends."
                ),
                ChatMessage(role="user", content=markdown_table),
            ]
            response = self.llm.chat(messages)
            return response.message.content.strip()
        except Exception as e:  
            logger.error(f"Table summarization error: {e}")
            return "Unable to generate summary"
        
    def _plot_table(self, index_name, markdown_table: str):
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="""
                            You are an advanced language model assisting with data transformation. Below are tables provided in markdown format. Your task is to:

                            Extract  the key information from the tables.
                            Generate complete HTML code that visualizes the data using Plotly.js, including:
                            1. A <script> tag to include Plotly.js.
                            2. A <div> for rendering the chart.
                            3. A JavaScript block with the data converted from the markdown table into Plotly.js format, including x, y, type, and name attributes.

                            Requirements:

                            1. The output should be a standalone HTML file that can be copy-pasted and opened in a browser to visualize the chart.
                            2. Extract x (labels) from the first column of the markdown table and y (values) from subsequent columns.
                            3. Generate multiple datasets if the table has multiple numerical columns.
                            4. Use descriptive names for each dataset based on the column headers.
                            5. Make appropriate chart for the particular dataset given .
                            """
                ),
                ChatMessage(role="user", content=markdown_table),
            ]
            response = self.llm.chat(messages)
            plots_response = response.message.content.strip()
            print(f"HTML code by LLM: {plots_response}")
            # breakpoint()
            html_code = self.extract_html_code(index_name, plots_response)
            # breakpoint()
            return html_code
        
        except Exception as e:  
            logger.error(f"Table summarization error: {e}")
            return "Unable to generate summary"


    def _create_vector_index(self, documents: List[Document]) -> VectorStoreIndex:
        """
        Create a vector index from documents.

        Args:
            documents (List[Document]): Documents to index

        Returns:
            VectorStoreIndex: Created vector index
        """
        try:
            # Recreate collection with vector configuration
            self.qdrant_client.recreate_collection(
                collection_name="finance_agent_collection",
                vectors_config=rest.VectorParams(
                    size=768,  # Matches embedding model dimensionality
                    distance=rest.Distance.COSINE,
                )
            )

            storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            return VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )
        except Exception as e:
            logger.error(f"Vector indexing error: {e}")
            raise

    def list_files_in_directory(self, directory_path):
        """
        Returns a list of files in the given directory.

        Args:
            directory_path (str): Path to the directory to scan.

        Returns:
            list: List of file names in the directory.
        """
        try:
            # List all files in the directory
            files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
            return files
        except FileNotFoundError:
            print(f"Error: Directory '{directory_path}' does not exist.")
            return []
        except PermissionError:
            print(f"Error: Permission denied to access '{directory_path}'.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
        
    def parse_pdf(self, file_path: str, output_file: str = "extracted_headings_and_tables.md") -> Dict[str, str]:
        """
        Parse PDF, extract tables, generate summaries, and index data.

        Args:
            file_path (str): Path to PDF file
            output_file (str, optional): Output filename. Defaults to "extracted_headings_and_tables.md"

        Returns:
            Dict[str, str]: Parsing result and output file path
        """
        # try:
            # Reset parsing status
        self.parsing_status = False

        # Parse PDF to markdown
        documents = self.pdf_parser.load_data(file_path)
        logger.info(f"Markdown extracted from PDF: {len(documents)} documents")

        # Extract tables with headings
        headings_and_tables = self._extract_headings_and_tables(documents)
        logger.info(f"Tables extracted: {len(headings_and_tables)}")

        # Generate summaries for tables
        table_with_summary = [
            {   

                "table": markdown_table, 
                "summary": self._summarize_table(markdown_table),
                "plot": self._plot_table(i , markdown_table)
            } 
            
            for i, markdown_table in enumerate(headings_and_tables)
        ]
        # breakpoint()

        # Save tables to output file
        output_path = os.path.join(self.output_dir, output_file)
        with open(output_path, "w", encoding="utf-8") as file:
            for item in table_with_summary:
                file.write(item["table"] + "\n\n")
                file.write("# Summary \n" + item["summary"]+ "\n\n")
        logger.info(f"Tables saved to {output_path}")

        # Prepare documents for vector indexing
        index_documents = [
            Document(
                text=data["summary"],
                metadata={"table": data["table"]}
            ) 
            for data in table_with_summary
        ]

        # Create vector index
        self._create_vector_index(index_documents)
        logger.info("Data indexed in vector database")

        self.parsing_status = True
        html_files = self.list_files_in_directory("./public/html_graphs")
        return {
            "message": "Parsing completed successfully", 
            # "output_file": f"http://localhost:8000/{output_path}",
            "html_files": html_files,
            "table_with_summary": table_with_summary
        }

        # except Exception as e:
        #     logger.error(f"PDF parsing failed: {e}")
        #     self.parsing_status = False
        #     raise RuntimeError(f"Parsing error: {str(e)}")

    def is_parsing_complete(self) -> bool:
        """
        Check if parsing is complete.

        Returns:
            bool: Parsing status
        """
        return self.parsing_status

# Example usage
if __name__ == "__main__":
    # Replace with your actual API keys
    PDF_API_KEY = "your_pdf_parse_api_key"
    LLM_API_KEY = "your_llm_api_key"

    parser = PDFParsingService(
        pdf_api_key=PDF_API_KEY, 
        llm_api_key=LLM_API_KEY
    )

    result = parser.parse_pdf("sample.pdf")
    print(result)