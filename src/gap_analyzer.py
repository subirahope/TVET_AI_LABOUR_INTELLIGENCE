"""
gap_analyzer.py
Phase 3: Skills Gap Analysis

Thesis Requirements:
- RQ2.1: Compare market-demand skills against TVET curriculum skills
- Identifies gaps between what employers want and what TVET teaches
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter

class GapAnalyzer:
    """
    Analyzes gaps between labour market demand and TVET curriculum supply.
    
    Methods:
    - compare_skills(): Identify missing or underrepresented skills
    - calculate_gap_score(): Quantify gap severity
    - generate_gap_report(): Create comprehensive gap analysis
    """
    
    def __init__(self):
        self.market_skills = []
        self.curriculum_skills = []
        self.gap_matrix = None
    
    def set_market_skills(self, skills_list: List[str]):
        """Set the list of skills extracted from job postings"""
        self.market_skills = skills_list
        return self
    
    def set_curriculum_skills(self, skills_list: List[str]):
        """Set the list of skills extracted from curriculum documents"""
        self.curriculum_skills = skills_list
        return self
    
    def set_market_frequencies(self, freq_dict: Dict):
        """Set skill frequencies from job market"""
        self.market_freq = freq_dict
        return self
    
    def set_curriculum_frequencies(self, freq_dict: Dict):
        """Set skill frequencies from curriculum"""
        self.curriculum_freq = freq_dict
        return self
    
    def identify_missing_skills(self) -> List[Tuple[str, int]]:
        """
        Identify skills that appear in market but NOT in curriculum.
        Returns list of (skill, market_frequency)
        """
        market_set = set(self.market_skills)
        curriculum_set = set(self.curriculum_skills)
        
        missing = market_set - curriculum_set
        
        # Get frequencies for missing skills
        if hasattr(self, 'market_freq'):
            missing_with_freq = [(skill, self.market_freq.get(skill, 0)) 
                                  for skill in missing]
            missing_with_freq.sort(key=lambda x: x[1], reverse=True)
            return missing_with_freq
        else:
            return [(skill, 0) for skill in missing]
    
    def identify_underrepresented_skills(self, threshold: float = 0.3) -> List[Tuple[str, float, float]]:
        """
        Identify skills that appear in both but are underrepresented in curriculum.
        Underrepresented = curriculum frequency < threshold * market frequency
        
        Returns list of (skill, market_freq, curriculum_freq)
        """
        if not hasattr(self, 'market_freq') or not hasattr(self, 'curriculum_freq'):
            return []
        
        underrepresented = []
        market_set = set(self.market_freq.keys())
        curriculum_set = set(self.curriculum_freq.keys())
        common = market_set.intersection(curriculum_set)
        
        for skill in common:
            market_freq = self.market_freq[skill]
            curriculum_freq = self.curriculum_freq[skill]
            
            if curriculum_freq < threshold * market_freq:
                underrepresented.append((skill, market_freq, curriculum_freq))
        
        underrepresented.sort(key=lambda x: x[1], reverse=True)
        return underrepresented
    
    def calculate_gap_score(self, 
                            market_freq: int, 
                            curriculum_freq: int = 0,
                            max_market_freq: int = 100) -> float:
        """
        Calculate gap score for a single skill.
        
        Formula: gap = (market_freq - curriculum_freq) / max_market_freq
        Range: 0 (no gap) to 1 (complete gap)
        
        For skills not in curriculum: curriculum_freq = 0
        """
        gap = (market_freq - curriculum_freq) / max_market_freq
        return max(0, min(1, gap))  # Clamp between 0 and 1
    
    def generate_gap_matrix(self, max_market_freq: int = None) -> pd.DataFrame:
        """
        Generate complete gap matrix comparing all skills.
        
        Returns DataFrame with columns:
        - skill
        - market_frequency
        - curriculum_frequency
        - gap_score
        - status (missing / underrepresented / aligned)
        """
        if not hasattr(self, 'market_freq'):
            print("Error: Market frequencies not set")
            return None
        
        # Determine max frequency for normalization
        if max_market_freq is None:
            max_market_freq = max(self.market_freq.values()) if self.market_freq else 1
        
        all_skills = set(self.market_freq.keys())
        if hasattr(self, 'curriculum_freq'):
            all_skills.update(self.curriculum_freq.keys())
        
        gap_data = []
        for skill in all_skills:
            market_freq = self.market_freq.get(skill, 0)
            curriculum_freq = self.curriculum_freq.get(skill, 0)
            
            gap_score = self.calculate_gap_score(market_freq, curriculum_freq, max_market_freq)
            
            # Determine status
            if curriculum_freq == 0:
                status = "missing"
            elif gap_score > 0.5:
                status = "severe_gap"
            elif gap_score > 0.2:
                status = "moderate_gap"
            else:
                status = "aligned"
            
            gap_data.append({
                'skill': skill,
                'market_frequency': market_freq,
                'curriculum_frequency': curriculum_freq,
                'gap_score': round(gap_score, 3),
                'status': status
            })
        
        self.gap_matrix = pd.DataFrame(gap_data)
        self.gap_matrix = self.gap_matrix.sort_values('gap_score', ascending=False)
        
        return self.gap_matrix
    
    def get_top_gaps(self, n: int = 10, status_filter: str = None) -> pd.DataFrame:
        """
        Get top N skills gaps.
        
        Parameters:
        - n: Number of gaps to return
        - status_filter: 'missing', 'severe_gap', 'moderate_gap', 'aligned', or None for all
        """
        if self.gap_matrix is None:
            self.generate_gap_matrix()
        
        df = self.gap_matrix
        if status_filter:
            df = df[df['status'] == status_filter]
        
        return df.head(n)
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive gap analysis report.
        """
        if self.gap_matrix is None:
            self.generate_gap_matrix()
        
        df = self.gap_matrix
        
        # Count by status
        status_counts = df['status'].value_counts().to_dict()
        
        # Calculate average gap score
        avg_gap = df['gap_score'].mean()
        
        # Get top 5 missing skills
        top_missing = df[df['status'] == 'missing'].head(5)[['skill', 'market_frequency']].to_dict('records')
        
        # Get top 5 severe gaps
        top_severe = df[df['status'] == 'severe_gap'].head(5)[['skill', 'market_frequency', 'curriculum_frequency', 'gap_score']].to_dict('records')
        
        return {
            'total_skills_analyzed': len(df),
            'status_summary': status_counts,
            'average_gap_score': avg_gap,
            'top_missing_skills': top_missing,
            'top_severe_gaps': top_severe,
            'recommendation_priority': 'High' if avg_gap > 0.4 else 'Medium' if avg_gap > 0.2 else 'Low'
        }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    print("Testing Gap Analyzer...")
    
    # Sample data
    market_skills = ['python', 'aws', 'docker', 'kubernetes', 'sql', 'machine learning', 
                     'tensorflow', 'azure', 'python', 'aws', 'docker', 'sql', 'python', 'aws']
    
    curriculum_skills = ['python', 'sql', 'java', 'javascript', 'html', 'css', 'python', 'sql']
    
    # Create frequency dictionaries
    market_freq = dict(Counter(market_skills))
    curriculum_freq = dict(Counter(curriculum_skills))
    
    print("\n1. Market skill frequencies:")
    print(market_freq)
    
    print("\n2. Curriculum skill frequencies:")
    print(curriculum_freq)
    
    # Initialize analyzer
    analyzer = GapAnalyzer()
    analyzer.set_market_frequencies(market_freq)
    analyzer.set_curriculum_frequencies(curriculum_freq)
    
    # Generate gap matrix
    print("\n3. Generating gap matrix...")
    gap_df = analyzer.generate_gap_matrix(max_market_freq=10)
    print(gap_df)
    
    # Get missing skills
    print("\n4. Missing skills (in market but not curriculum):")
    missing = analyzer.get_top_gaps(n=10, status_filter='missing')
    print(missing[['skill', 'market_frequency']])
    
    # Get top gaps overall
    print("\n5. Top 5 overall gaps:")
    top_gaps = analyzer.get_top_gaps(n=5)
    for _, row in top_gaps.iterrows():
        print(f"   {row['skill']}: gap_score={row['gap_score']} ({row['status']})")
    
    # Generate report
    print("\n6. Gap Analysis Report:")
    report = analyzer.generate_report()
    print(f"   Total skills analyzed: {report['total_skills_analyzed']}")
    print(f"   Status summary: {report['status_summary']}")
    print(f"   Average gap score: {report['average_gap_score']:.2f}")
    print(f"   Recommendation priority: {report['recommendation_priority']}")
    
    print("\nGap Analyzer ready!")