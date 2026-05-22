"""
nlp_pipeline.py
Phase 2: NLP Skill Extraction Pipeline

Thesis Requirements:
- RQ1.2: Extract skills from job descriptions using NLP
- RQ1.3: Normalize extracted skills to ESCO taxonomy
"""

import re
import pandas as pd
from typing import List, Dict, Set
import json
from pathlib import Path

class NLPPipeline:
    """
    Natural Language Processing pipeline for skill extraction and normalization.
    
    Stages:
    1. Pre-processing (clean text)
    2. Skill extraction (NER + keyword matching)
    3. Skill normalization (map to standard taxonomy)
    """
    
    def __init__(self):
        # Define known skills (expandable)
        self.skill_keywords = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'r', 'matlab'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'cassandra', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'cloud computing', 'serverless', 'lambda', 'ec2', 's3'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'gitlab', 'ci/cd', 'terraform', 'ansible', 'github actions'],
            'data_science': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'data science', 'machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'computer vision'],
            'cybersecurity': ['cybersecurity', 'network security', 'penetration testing', 'siem', 'firewall', 'encryption', 'security audit', 'risk assessment'],
            'soft_skills': ['communication', 'leadership', 'problem solving', 'teamwork', 'project management', 'agile', 'scrum'],
            'engineering': ['plc', 'scada', 'automation', 'cad', 'solidworks', 'autocad', 'mechanical', 'electrical', 'civil', 'instrumentation']
        }
        
        # Flatten skills for easy lookup
        self.all_skills = set()
        for category, skills in self.skill_keywords.items():
            self.all_skills.update(skills)
        
        # ESCO taxonomy mapping (simplified - can be expanded)
        self.esco_mapping = self._load_esco_mapping()
        
        # Track extracted skills
        self.extracted_skills = []
        self.normalized_skills = []
    
    def _load_esco_mapping(self) -> Dict:
        """
        Load ESCO taxonomy mapping.
        For now, we use a simplified mapping.
        In production, this would load from official ESCO JSON/CSV.
        """
        # Simplified ESCO mapping (skill_variation -> canonical_skill)
        esco_map = {
            # Python variations
            'python': 'Python',
            'python programming': 'Python',
            'python developer': 'Python',
            'python coding': 'Python',
            
            # SQL variations
            'sql': 'SQL',
            'structured query language': 'SQL',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            
            # Cloud variations
            'aws': 'Amazon Web Services',
            'amazon web services': 'Amazon Web Services',
            'azure': 'Microsoft Azure',
            'microsoft azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform',
            
            # Machine Learning variations
            'ml': 'Machine Learning',
            'machine learning': 'Machine Learning',
            'ai': 'Artificial Intelligence',
            'artificial intelligence': 'Artificial Intelligence',
            'deep learning': 'Deep Learning',
            
            # Data Science variations
            'data science': 'Data Science',
            'data analytics': 'Data Analytics',
            'data analysis': 'Data Analytics',
        }
        return esco_map
    
    def preprocess_text(self, text: str) -> str:
        """
        Stage 1: Clean and preprocess text.
        - Lowercase
        - Remove special characters
        - Remove extra whitespace
        """
        if not isinstance(text, str):
            return ""
        
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)       # Remove extra spaces
        return text.strip()
    
    def extract_skills_keyword(self, text: str) -> List[str]:
        """
        Stage 2a: Extract skills using keyword matching.
        This is the primary method for the prototype.
        """
        if not text:
            return []
        
        processed_text = self.preprocess_text(text)
        found_skills = []
        
        for skill in self.all_skills:
            if skill in processed_text:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_skills_ner(self, text: str) -> List[str]:
        """
        Stage 2b: Extract skills using NER (Named Entity Recognition).
        For prototype, this uses keyword matching.
        In production, this would use a BERT-based NER model.
        """
        # For now, use keyword extraction as NER placeholder
        # TODO: Integrate actual NER model (JobBERT) later
        return self.extract_skills_keyword(text)
    
    def normalize_skill(self, skill: str) -> str:
        """
        Stage 3: Normalize skill to ESCO taxonomy.
        Maps variations to canonical skill names.
        """
        skill_lower = skill.lower()
        if skill_lower in self.esco_mapping:
            return self.esco_mapping[skill_lower]
        return skill.capitalize()
    
    def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalize a list of skills.
        """
        return [self.normalize_skill(s) for s in skills]
    
    def process_job_description(self, description: str) -> Dict:
        """
        Complete pipeline for a single job description.
        
        Returns:
        - original_text
        - extracted_skills (raw)
        - normalized_skills (ESCO mapped)
        - skill_count
        """
        if not description:
            return {
                'original_text': '',
                'extracted_skills': [],
                'normalized_skills': [],
                'skill_count': 0
            }
        
        # Extract skills
        extracted = self.extract_skills_ner(description)
        
        # Normalize skills
        normalized = self.normalize_skills(extracted)
        
        return {
            'original_text': description[:200] + "..." if len(description) > 200 else description,
            'extracted_skills': extracted,
            'normalized_skills': normalized,
            'skill_count': len(set(normalized))
        }
    
    def process_dataframe(self, df: pd.DataFrame, text_column: str = 'description') -> pd.DataFrame:
        """
        Process entire DataFrame of job postings.
        
        Adds columns:
        - extracted_skills
        - normalized_skills
        - skill_count
        """
        if df is None or text_column not in df.columns:
            print(f"Error: Column '{text_column}' not found in DataFrame")
            return df
        
        # Apply pipeline to each row
        results = df[text_column].apply(self.process_job_description)
        
        df['extracted_skills'] = results.apply(lambda x: x['extracted_skills'])
        df['normalized_skills'] = results.apply(lambda x: x['normalized_skills'])
        df['skill_count'] = results.apply(lambda x: x['skill_count'])
        
        return df
    
    def get_skill_frequencies(self, df: pd.DataFrame) -> Dict:
        """
        Calculate frequency of each skill across all job postings.
        """
        if df is None or 'normalized_skills' not in df.columns:
            return {}
        
        all_skills = []
        for skills_list in df['normalized_skills']:
            all_skills.extend(skills_list)
        
        from collections import Counter
        return dict(Counter(all_skills))
    
    def get_top_skills(self, df: pd.DataFrame, n: int = 10) -> List[tuple]:
        """
        Get top N most frequent skills.
        """
        frequencies = self.get_skill_frequencies(df)
        sorted_skills = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:n]
    
    def get_skill_categories(self, skill: str) -> str:
        """
        Determine which category a skill belongs to.
        """
        skill_lower = skill.lower()
        for category, skills in self.skill_keywords.items():
            if skill_lower in skills:
                return category
        return 'other'

# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add parent directory to path so we can import src modules
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    print("Testing NLP Pipeline...")
    
    # Initialize pipeline
    nlp = NLPPipeline()
    
    # Test description
    test_desc = """
    We are looking for a Senior Python Developer with experience in AWS, Docker, and Kubernetes.
    Must have strong SQL skills and knowledge of machine learning algorithms.
    Experience with TensorFlow or PyTorch is a plus.
    """
    
    print("\n1. Testing single description:")
    print(f"Input: {test_desc[:100]}...")
    
    result = nlp.process_job_description(test_desc)
    print(f"Extracted skills: {result['extracted_skills']}")
    print(f"Normalized skills: {result['normalized_skills']}")
    
    # Test DataFrame
    print("\n2. Testing DataFrame processing:")
    from src.data_loader import DataLoader
    
    loader = DataLoader()
    df = loader.generate_sample_job_data()
    
    print(f"Original DataFrame: {len(df)} rows")
    print(df[['title', 'description']].head())
    
    # Process
    df_processed = nlp.process_dataframe(df, text_column='description')
    
    print(f"\nProcessed DataFrame columns: {df_processed.columns.tolist()}")
    print(f"\nExtracted skills sample:")
    for i, row in df_processed.head(3).iterrows():
        print(f"  {row['title']}: {row['extracted_skills']}")
    
    # Get top skills
    top_skills = nlp.get_top_skills(df_processed)
    print(f"\nTop skills: {top_skills}")
    
    print("\nNLP Pipeline ready!")