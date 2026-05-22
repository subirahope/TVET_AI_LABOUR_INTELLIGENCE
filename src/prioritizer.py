"""
prioritizer.py
Phase 4: Multi-Criteria Gap Prioritization

Thesis Requirements:
- RQ2.2: Prioritize gaps based on frequency, growth, curriculum absence, and trainability
- Outputs ranked list of skills recommended for short course development
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class GapPrioritizer:
    """
    Prioritizes skills gaps using multi-criteria scoring.
    
    Scoring dimensions:
    1. Frequency Score (0-1): How often skill appears in job postings
    2. Growth Score (0-1): Rate of increase in demand over time
    3. Curriculum Gap Score (0-1): How absent/insufficient in current curricula
    4. Trainability Score (0-1): Feasibility of teaching in 2-6 months
    """
    
    def __init__(self):
        self.scores = {}
        self.prioritized_gaps = None
        self.weights = {
            'frequency': 0.35,
            'growth': 0.25,
            'curriculum_gap': 0.25,
            'trainability': 0.15
        }
    
    def set_weights(self, frequency: float = 0.35, growth: float = 0.25, 
                    curriculum_gap: float = 0.25, trainability: float = 0.15):
        """Set custom weights for prioritization dimensions"""
        total = frequency + growth + curriculum_gap + trainability
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0. Current sum: {total}")
        
        self.weights = {
            'frequency': frequency,
            'growth': growth,
            'curriculum_gap': curriculum_gap,
            'trainability': trainability
        }
    
    def calculate_frequency_score(self, market_freq: int, max_freq: int = 100) -> float:
        """Calculate normalized frequency score. Higher frequency = higher score."""
        return min(1.0, market_freq / max_freq)
    
    def calculate_growth_score(self, growth_rate: float) -> float:
        """Calculate growth score based on percentage increase."""
        return min(1.0, growth_rate / 0.5)
    
    def calculate_curriculum_gap_score(self, market_freq: int, curriculum_freq: int, 
                                        max_freq: int = 100) -> float:
        """Calculate curriculum gap score. Higher gap = higher score."""
        if market_freq == 0:
            return 0.0
        diff = (market_freq - curriculum_freq) / max_freq
        return min(1.0, max(0.0, diff))
    
    def calculate_trainability_score(self, skill: str) -> float:
        """Calculate trainability score based on skill characteristics."""
        high_trainability = [
            'python', 'sql', 'aws', 'azure', 'docker', 'kubernetes', 'git',
            'tableau', 'power bi', 'excel', 'javascript', 'html', 'css',
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch'
        ]
        
        medium_trainability = [
            'machine learning', 'data science', 'cybersecurity', 'cloud computing',
            'project management', 'agile', 'scrum', 'communication', 'leadership',
            'problem solving', 'teamwork'
        ]
        
        low_trainability = [
            'civil engineering', 'mechanical engineering', 'electrical engineering',
            'professional judgment', 'strategic planning'
        ]
        
        skill_lower = skill.lower()
        
        if any(s in skill_lower for s in high_trainability):
            return 1.0
        elif any(s in skill_lower for s in medium_trainability):
            return 0.5
        elif any(s in skill_lower for s in low_trainability):
            return 0.2
        else:
            return 0.6
    
    def calculate_total_score(self, skill: str, market_freq: int, curriculum_freq: int,
                               growth_rate: float = 0.0, max_freq: int = 100) -> float:
        """Calculate total priority score for a single skill."""
        freq_score = self.calculate_frequency_score(market_freq, max_freq)
        growth_score = self.calculate_growth_score(growth_rate)
        gap_score = self.calculate_curriculum_gap_score(market_freq, curriculum_freq, max_freq)
        train_score = self.calculate_trainability_score(skill)
        
        total = (freq_score * self.weights['frequency']) + \
                (growth_score * self.weights['growth']) + \
                (gap_score * self.weights['curriculum_gap']) + \
                (train_score * self.weights['trainability'])
        
        return round(total, 3)
    
    def prioritize_gaps(self, gap_matrix: pd.DataFrame, 
                        growth_rates: Optional[Dict[str, float]] = None,
                        max_freq: int = None) -> pd.DataFrame:
        """
        Prioritize gaps from gap matrix.
        
        Parameters:
        - gap_matrix: DataFrame with skills, market_frequency, curriculum_frequency
        - growth_rates: Dict of skill -> growth_rate (0-1)
        - max_freq: Maximum frequency for normalization
        
        Returns DataFrame with priority scores and ranks
        """
        if gap_matrix is None or len(gap_matrix) == 0:
            print("Error: No gap matrix provided")
            return None
        
        if max_freq is None:
            max_freq = gap_matrix['market_frequency'].max()
        
        if max_freq == 0:
            max_freq = 1
        
        # Calculate scores for each skill
        scores = []
        for _, row in gap_matrix.iterrows():
            skill = row['skill']
            market_freq = row['market_frequency']
            curriculum_freq = row.get('curriculum_frequency', 0)
            gap_score = row.get('gap_score', 0)
            growth_rate = growth_rates.get(skill, 0.0) if growth_rates else 0.0
            
            total_score = self.calculate_total_score(
                skill, market_freq, curriculum_freq, growth_rate, max_freq
            )
            
            # Determine priority tier
            if total_score >= 0.7:
                priority = "High"
            elif total_score >= 0.4:
                priority = "Medium"
            else:
                priority = "Low"
            
            scores.append({
                'skill': skill,
                'market_frequency': market_freq,
                'curriculum_frequency': curriculum_freq,
                'gap_score': gap_score,
                'priority_score': total_score,
                'priority_tier': priority
            })
        
        # Create DataFrame and sort by score
        self.prioritized_gaps = pd.DataFrame(scores)
        self.prioritized_gaps = self.prioritized_gaps.sort_values('priority_score', ascending=False)
        self.prioritized_gaps['rank'] = range(1, len(self.prioritized_gaps) + 1)
        
        return self.prioritized_gaps
    
    def get_high_priority_gaps(self, n: int = None) -> pd.DataFrame:
        """Get high priority gaps (priority_tier = 'High')"""
        if self.prioritized_gaps is None:
            return None
        
        high = self.prioritized_gaps[self.prioritized_gaps['priority_tier'] == 'High']
        if n:
            return high.head(n)
        return high
    
    def get_recommendations(self, n: int = 10) -> List[Dict]:
        """Generate short course recommendations from prioritized gaps."""
        if self.prioritized_gaps is None:
            return []
        
        recommendations = []
        for _, row in self.prioritized_gaps.head(n).iterrows():
            recommendations.append({
                'skill': row['skill'],
                'priority_score': row['priority_score'],
                'priority_tier': row['priority_tier'],
                'market_frequency': row['market_frequency'],
                'curriculum_frequency': row['curriculum_frequency'],
                'justification': self._generate_justification(row)
            })
        
        return recommendations
    
    def _generate_justification(self, row: pd.Series) -> str:
        """Generate justification text for a recommendation"""
        if row['curriculum_frequency'] == 0:
            return f"Skill '{row['skill']}' appears {row['market_frequency']} times in job postings but is completely missing from current curriculum."
        else:
            return f"Skill '{row['skill']}' appears {row['market_frequency']} times in job postings but only {row['curriculum_frequency']} times in curriculum. High demand gap."
    
    def get_summary(self) -> Dict:
        """Get summary of prioritization results"""
        if self.prioritized_gaps is None:
            return {}
        
        return {
            'total_gaps_analyzed': len(self.prioritized_gaps),
            'high_priority_count': len(self.prioritized_gaps[self.prioritized_gaps['priority_tier'] == 'High']),
            'medium_priority_count': len(self.prioritized_gaps[self.prioritized_gaps['priority_tier'] == 'Medium']),
            'low_priority_count': len(self.prioritized_gaps[self.prioritized_gaps['priority_tier'] == 'Low']),
            'average_priority_score': self.prioritized_gaps['priority_score'].mean(),
            'weights_used': self.weights.copy()
        }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    print("Testing Gap Prioritizer...")
    
    # Sample gap matrix
    gap_matrix = pd.DataFrame({
        'skill': ['python', 'aws', 'docker', 'kubernetes', 'sql', 'tensorflow', 
                  'azure', 'machine learning', 'cybersecurity', 'leadership'],
        'market_frequency': [45, 38, 32, 28, 25, 22, 20, 18, 15, 10],
        'curriculum_frequency': [30, 5, 0, 0, 20, 0, 2, 8, 3, 5]
    })
    
    # Sample growth rates
    growth_rates = {
        'python': 0.12,
        'aws': 0.35,
        'docker': 0.28,
        'kubernetes': 0.42,
        'sql': 0.05,
        'tensorflow': 0.18,
        'azure': 0.22,
        'machine learning': 0.15,
        'cybersecurity': 0.30,
        'leadership': 0.08
    }
    
    print("\n1. Sample gap matrix:")
    print(gap_matrix)
    
    # Initialize prioritizer
    prioritizer = GapPrioritizer()
    
    # Customize weights (optional)
    prioritizer.set_weights(frequency=0.35, growth=0.25, curriculum_gap=0.25, trainability=0.15)
    print(f"\n2. Using weights: {prioritizer.weights}")
    
    # Prioritize gaps
    print("\n3. Prioritizing gaps...")
    prioritized = prioritizer.prioritize_gaps(gap_matrix, growth_rates, max_freq=50)
    if prioritized is not None:
        print(prioritized[['rank', 'skill', 'priority_score', 'priority_tier']])
    
    print("\nGap Prioritizer ready!")