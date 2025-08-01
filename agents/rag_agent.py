import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
try:
    import numpy as np
except ImportError:
    raise ImportError("Numpy is required. Please install it using 'pip install numpy'")

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    raise ImportError("Scikit-learn is required. Please install it using 'pip install scikit-learn'")

import pickle
from agents.base_agent import BaseAgent
from config.sahayak_config import SahayakConfig
import google.generativeai as genai

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Sentence-transformers is required. Please install it using 'pip install sentence-transformers'")

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 is required. Please install it using 'pip install PyPDF2'")

try:
    import docx
except ImportError:
    raise ImportError("python-docx is required. Please install it using 'pip install python-docx'")

try:
    import pandas as pd
except ImportError:
    raise ImportError("Pandas is required. Please install it using 'pip install pandas'")

import json
import re

class RAGAgent(BaseAgent):
    """Agent for Retrieval Augmented Generation with multi-document support"""
    
    def __init__(self):
        super().__init__(
            name="RAG Assistant",
            description="Handles context-aware responses using multi-document knowledge base",
            model=SahayakConfig.DEFAULT_MODEL
        )
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        try:
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.chunk_size = 500
            self.chunk_overlap = 50
            self.knowledge_base = {
                'documents': [],  # List of document texts
                'embeddings': None,  # numpy array of embeddings
                'metadata': []  # List of document metadata
            }
            
            # Create uploads directory
            self.uploads_dir = os.path.join(self._get_root_folder(), "data", "uploads")
            os.makedirs(self.uploads_dir, exist_ok=True)
            
        except Exception as e:
            self.logger.error(f"Error initializing RAG Agent: {str(e)}")
            raise
        
    def _get_root_folder(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _get_knowledge_base_path(self) -> str:
        return os.path.join(self.kb_dir, "knowledge_base.pkl")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        return text

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
        return text

    def _extract_text_from_excel(self, file_path: str) -> str:
        """Extract text from Excel file"""
        text = ""
        try:
            df = pd.read_excel(file_path)
            # Convert DataFrame to string representation
            text = df.to_string(index=False)
        except Exception as e:
            self.logger.error(f"Error extracting text from Excel {file_path}: {str(e)}")
        return text

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file types"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self._extract_text_from_docx(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return self._extract_text_from_excel(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), indent=2)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > self.chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def _compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for a list of texts"""
        return self.embedding_model.encode(texts, show_progress_bar=True)

    def initialize_knowledge_base(self, uploads_dir: str = None) -> Dict:
        """Initialize knowledge base from uploaded documents"""
        try:
            if uploads_dir is None:
                uploads_dir = self.uploads_dir
            
            self.logger.info(f"Processing documents from: {uploads_dir}")
            
            # Reset knowledge base
            self.knowledge_base = {
                'documents': [],
                'embeddings': None,
                'metadata': []
            }

            if not os.path.exists(uploads_dir):
                return {
                    'status': 'error',
                    'error': 'No documents found. Please upload some documents first.',
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

            documents = []
            metadata = []
            
            # Process all files in uploads directory
            for file in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, file)
                try:
                    self.logger.info(f"Processing file: {file}")
                    content = self._extract_text_from_file(file_path)
                    
                    if content.strip():
                        chunks = self._chunk_text(content)
                        documents.extend(chunks)
                        
                        # Add metadata for each chunk
                        for chunk_idx, chunk in enumerate(chunks):
                            metadata.append({
                                'source_file': file,
                                'chunk_index': chunk_idx + 1,
                                'created_at': datetime.now().isoformat()
                            })
                        self.logger.info(f"Added {len(chunks)} chunks from {file}")
                    else:
                        self.logger.warning(f"No content extracted from {file}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing file {file}: {str(e)}")

            if documents:
                # Compute embeddings for all chunks
                embeddings = self._compute_embeddings(documents)
                
                self.knowledge_base = {
                    'documents': documents,
                    'embeddings': embeddings,
                    'metadata': metadata
                }
                
                return {
                    'status': 'success',
                    'num_documents': len(set(m['source_file'] for m in metadata)),
                    'num_chunks': len(documents),
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }
            else:
                return {
                    'status': 'error',
                    'error': 'No content could be extracted from the uploaded documents.',
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error processing documents: {error_msg}")
            return {
                'status': 'error',
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

    def add_document(self, file_path: str) -> Dict:
        """Add a new document to the knowledge base"""
        try:
            self.logger.info(f"Processing document: {file_path}")
            
            if not os.path.exists(file_path):
                return {
                    'status': 'error',
                    'error': f'File not found: {file_path}',
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

            content = self._extract_text_from_file(file_path)
            if not content.strip():
                return {
                    'status': 'error',
                    'error': f'No content extracted from file: {file_path}',
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

            chunks = self._chunk_text(content)
            self.logger.info(f"Created {len(chunks)} chunks from document")
            
            new_embeddings = self._compute_embeddings(chunks)
            file_extension = os.path.splitext(file_path)[1].lower()

            # Add new chunks and embeddings
            if self.knowledge_base['embeddings'] is None:
                self.knowledge_base['embeddings'] = new_embeddings
            else:
                self.knowledge_base['embeddings'] = np.vstack([
                    self.knowledge_base['embeddings'],
                    new_embeddings
                ])

            self.knowledge_base['documents'].extend(chunks)
            
            for chunk_idx, _ in enumerate(chunks):
                self.knowledge_base['metadata'].append({
                    'source_file': os.path.basename(file_path),  # Store just the filename
                    'file_type': file_extension,
                    'chunk_index': chunk_idx,
                    'created_at': datetime.now().isoformat()
                })

            # Auto-save after adding document
            self.save_knowledge_base()

            result = {
                'status': 'success',
                'file_path': file_path,
                'file_type': file_extension,
                'num_chunks': len(chunks),
                'total_documents': len(set(m['source_file'] for m in self.knowledge_base['metadata'])),
                'total_chunks': len(self.knowledge_base['documents']),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

            self.log_interaction(
                "Document addition",
                f"Added document: {file_path}",
                {'num_chunks': len(chunks)}
            )

            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error adding document {file_path}: {error_msg}")
            return {
                'status': 'error',
                'error': error_msg,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

    def generate_response(self, query: str, num_chunks: int = 3) -> Dict:
        """Generate a context-aware response"""
        try:
            if not self.knowledge_base['documents']:
                return {
                    'status': 'error',
                    'error': 'Knowledge base is empty. Please upload some documents first.',
                    'response': 'No documents found in knowledge base. Please upload documents to search through.',
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

            # Get query embedding
            query_embedding = self._compute_embeddings([query])

            # Calculate similarities
            similarities = cosine_similarity(
                query_embedding,
                self.knowledge_base['embeddings']
            )[0]

            # Get top k chunks and their metadata
            top_indices = np.argsort(similarities)[-num_chunks:][::-1]
            relevant_chunks = [self.knowledge_base['documents'][i] for i in top_indices]
            relevant_metadata = [self.knowledge_base['metadata'][i] for i in top_indices]
            
            # Format sources information
            sources = [f"{meta['source_file']} (chunk {meta['chunk_index'] + 1})" 
                      for meta in relevant_metadata]
            
            # Construct prompt with context
            prompt = f"""Based on the following context and question, provide a detailed response:

Context:
{' '.join(relevant_chunks)}

Question: {query}

Provide a response that incorporates relevant information from the context while staying focused on the question."""

            response = self._make_request(prompt)
            
            result = {
                'status': 'success',
                'query': query,
                'response': response,
                'raw_output': response,  # Add this for compatibility
                'sources': sources,
                'num_chunks_used': len(relevant_chunks),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

            self.log_interaction(
                "Response generation",
                response,
                {
                    'query': query,
                    'num_chunks': len(relevant_chunks),
                    'sources': sources
                }
            )

            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error in generate_response: {error_msg}")
            return {
                'status': 'error',
                'error': error_msg,
                'response': f"Error processing your request: {error_msg}",
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

    def save_knowledge_base(self) -> Dict:
        """Save knowledge base to disk"""
        try:
            save_path = self._get_knowledge_base_path()
            
            with open(save_path, 'wb') as f:
                pickle.dump(self.knowledge_base, f)
            
            result = {
                'status': 'success',
                'save_path': save_path,
                'num_documents': len(set(m['source_file'] for m in self.knowledge_base['metadata'])),
                'num_chunks': len(self.knowledge_base['documents']),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

            self.log_interaction(
                "Knowledge base saving",
                f"Saved to {save_path}",
                result
            )

            return result

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

    def load_knowledge_base(self) -> Dict:
        """Load knowledge base from disk"""
        try:
            load_path = self._get_knowledge_base_path()
            
            if not os.path.exists(load_path):
                return {
                    'status': 'error',
                    'error': 'No saved knowledge base found',
                    'timestamp': datetime.now().isoformat(),
                    'agent': self.name
                }

            with open(load_path, 'rb') as f:
                self.knowledge_base = pickle.load(f)
            
            result = {
                'status': 'success',
                'load_path': load_path,
                'num_documents': len(set(m['source_file'] for m in self.knowledge_base['metadata'])),
                'num_chunks': len(self.knowledge_base['documents']),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }

            self.log_interaction(
                "Knowledge base loading",
                f"Loaded from {load_path}",
                result
            )

            return result

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }