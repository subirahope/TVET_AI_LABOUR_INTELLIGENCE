"""
data_loader.py
Phase 1: Data Ingestion Module
Handles loading of job postings, curriculum documents, and expert validation data.

Thesis Requirements:
- DC.1: Collect job postings from Kenyan platforms
- DC.2: Collect curriculum documents from partner TVET institutions
- DC.3: Collect expert validation data
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import io
import PyPDF2
from datetime import datetime
import json

class DataLoader:
    """
    Handles all data loading for the TVET Labour Market Intelligence System.
    
    Supports:
    - Job postings from CSV/Excel files
    - Curriculum documents from PDF/TXT files
    - Expert validation responses from CSV/JSON
    """
    
    def __init__(self):
        self.job_data = None
        self.curriculum_docs = []
        self.expert_data = None
        self.data_sources = {
            'job_postings': None,
            'curriculum_docs': 0,
            'expert_responses': 0
        }
    
    # ============================================================
    # JOB POSTING DATA (DC.1)
    # ============================================================
    
    def load_job_postings(self, uploaded_file):
        """
        Load job postings from CSV or Excel file.
        
        Expected columns:
        - title: Job title
        - description: Job description (for skill extraction)
        - company: Company name (optional)
        - location: Job location (optional)
        - date_posted: Posting date (optional)
        
        Returns:
        - DataFrame with job postings
        """
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    self.job_data = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    self.job_data = pd.read_excel(uploaded_file)
                else:
                    st.error("Unsupported file format. Please upload CSV or Excel.")
                    return None
                
                self.data_sources['job_postings'] = uploaded_file.name
                
                # Log the load
                st.success(f"Loaded {len(self.job_data)} job postings from {uploaded_file.name}")
                
                # Display column info for debugging
                st.info(f"Columns detected: {', '.join(self.job_data.columns)}")
                
                return self.job_data
                
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return None
        return None
    
    def get_job_sample(self, n=5):
        """Return first n job postings for preview"""
        if self.job_data is not None:
            return self.job_data.head(n)
        return None
    
    def get_job_statistics(self):
        """Return basic statistics about loaded job data"""
        if self.job_data is not None:
            return {
                'total_jobs': len(self.job_data),
                'columns': list(self.job_data.columns),
                'date_range': self._get_date_range()
            }
        return None
    
    def _get_date_range(self):
        """Extract date range if date column exists"""
        if self.job_data is not None:
            date_cols = ['date', 'posted_date', 'date_posted', 'published_at', 'created']
            for col in date_cols:
                if col in self.job_data.columns:
                    try:
                        dates = pd.to_datetime(self.job_data[col])
                        return f"{dates.min().date()} to {dates.max().date()}"
                    except:
                        pass
        return "Not specified"
    
    # ============================================================
    # CURRICULUM DOCUMENTS (DC.2)
    # ============================================================
    
    def load_curriculum_document(self, uploaded_file, institution_name="Unknown"):
        """
        Load a curriculum document from PDF or TXT file.
        Extracts text for later NLP processing.
        
        Parameters:
        - uploaded_file: Streamlit uploaded file object
        - institution_name: Name of partner institution (for DC.2)
        
        Returns:
        - Extracted text from document
        """
        if uploaded_file is not None:
            try:
                text = ""
                
                if uploaded_file.type == "text/plain":
                    text = uploaded_file.read().decode("utf-8")
                    
                elif uploaded_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            
                else:
                    st.error(f"Unsupported file type: {uploaded_file.type}")
                    return None
                
                # Store document info
                doc_info = {
                    'filename': uploaded_file.name,
                    'institution': institution_name,
                    'text': text,
                    'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'skills': []  # Will be populated by NLP pipeline
                }
                self.curriculum_docs.append(doc_info)
                self.data_sources['curriculum_docs'] = len(self.curriculum_docs)
                
                st.success(f"Loaded curriculum document from {institution_name}: {uploaded_file.name}")
                st.info(f"Extracted {len(text)} characters of text")
                
                return text
                
            except Exception as e:
                st.error(f"Error loading PDF: {e}")
                return None
        return None
    
    def get_curriculum_summary(self):
        """Return summary of loaded curriculum documents"""
        if self.curriculum_docs:
            return {
                'total_documents': len(self.curriculum_docs),
                'institutions': [doc['institution'] for doc in self.curriculum_docs],
                'filenames': [doc['filename'] for doc in self.curriculum_docs]
            }
        return None
    
    # ============================================================
    # EXPERT VALIDATION DATA (DC.3)
    # ============================================================
    
    def load_expert_validation(self, uploaded_file):
        """
        Load expert validation responses from CSV or JSON.
        
        Expected CSV columns:
        - validator_name (optional)
        - institution
        - skill_gap_validated
        - rating (1-5)
        - comments
        """
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    self.expert_data = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    self.expert_data = pd.read_json(uploaded_file)
                else:
                    st.error("Please upload CSV or JSON file")
                    return None
                
                self.data_sources['expert_responses'] = len(self.expert_data)
                st.success(f"✅ Loaded {len(self.expert_data)} expert validation responses")
                
                return self.expert_data
                
            except Exception as e:
                st.error(f"Error loading expert data: {e}")
                return None
        return None
    
    def save_expert_response(self, response_data):
        """
        Save a single expert validation response to CSV.
        Called when expert submits form in dashboard.
        """
        import os
        
        # Define file path
        file_path = Path("data/raw/expert_validations.csv")
        
        # Create DataFrame from response
        df_new = pd.DataFrame([response_data])
        
        # Append to existing file or create new
        if file_path.exists():
            df_existing = pd.read_csv(file_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(file_path, index=False)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df_new.to_csv(file_path, index=False)
        
        self.data_sources['expert_responses'] += 1
        st.success("✅ Expert response saved successfully")
        
        return True
    
    # ============================================================
    # SAMPLE DATA GENERATION (For testing/demo)
    # ============================================================
    
    def generate_sample_job_data(self):
        """
        Generate sample job posting data for testing/demo.
        This is only for demonstration when no real data is available.
        """
        sample_data = pd.DataFrame({
            'title': [
                'Software Engineer',
                'Data Scientist',
                'Cloud Architect',
                'Cybersecurity Analyst',
                'Network Engineer'
            ],
            'description': [
                'Looking for Python, Django, and AWS experience. Must have strong problem-solving skills.',
                'Data Scientist needed with Python, SQL, and Machine Learning expertise. TensorFlow preferred.',
                'Cloud Architect required with AWS, Azure, and DevOps knowledge. Kubernetes experience a plus.',
                'Cybersecurity Analyst with Network Security, SIEM, and threat analysis skills. CISSP certified preferred.',
                'Network Engineer needed for Cisco routing, switching, and firewall configuration.'
            ],
            'company': ['Tech Corp', 'Data Inc', 'Cloud Solutions', 'SecureNet', 'NetWorks'],
            'location': ['Nairobi', 'Nairobi', 'Rift Valley', 'Nairobi', 'Western'],
            'date_posted': ['2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04', '2026-05-05']
        })
        
        self.job_data = sample_data
        self.data_sources['job_postings'] = "sample_data"
        
        return sample_data
    
    def get_data_summary(self):
        """Return complete summary of all loaded data"""
        return {
            'job_data': {
                'loaded': self.job_data is not None,
                'rows': len(self.job_data) if self.job_data is not None else 0,
                'source': self.data_sources['job_postings']
            },
            'curriculum_docs': {
                'loaded': len(self.curriculum_docs) > 0,
                'count': len(self.curriculum_docs),
                'institutions': [doc['institution'] for doc in self.curriculum_docs]
            },
            'expert_data': {
                'loaded': self.expert_data is not None,
                'responses': len(self.expert_data) if self.expert_data is not None else 0
            }
        }


# ============================================================
# TESTING (Run directly to verify module works)
# ============================================================

if __name__ == "__main__":
    print("Testing DataLoader module...")
    
    # Initialize
    loader = DataLoader()
    
    # Test sample data generation
    print("\n1. Generating sample job data...")
    sample = loader.generate_sample_job_data()
    print(f"   Generated {len(sample)} sample jobs")
    
    # Test summary
    print("\n2. Data summary:")
    summary = loader.get_data_summary()
    print(f"   Jobs loaded: {summary['job_data']['loaded']}")
    print(f"   Curriculum docs: {summary['curriculum_docs']['count']}")
    
    print("\nDataLoader module ready!")