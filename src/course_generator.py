"""
course_generator.py
Phase 5: Short Course Recommendation Generator

Thesis Requirements:
- RQ3.1: Generate course titles, learning outcomes, content modules
- RQ3.2: Provide implementation requirements (duration, assessment, prerequisites)
"""

import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

class CourseGenerator:
    """
    Generates short course recommendations from prioritized skills gaps.
    
    Each course includes:
    - Course title
    - Duration (weeks)
    - Target learner profile
    - Prerequisites
    - Learning outcomes (3-5)
    - Content modules
    - Assessment strategy
    - Implementation requirements
    """
    
    def __init__(self):
        self.courses = []
        self.course_templates = self._init_templates()
    
    def _init_templates(self) -> Dict:
        """Initialize course templates for common skills"""
        return {
            'python': {
                'title': 'Python Programming for Industry Applications',
                'duration': 8,
                'level': 'Beginner to Intermediate',
                'prerequisites': ['Basic computer literacy', 'Logical thinking'],
                'learning_outcomes': [
                    'Write, debug, and execute Python scripts independently',
                    'Work with data structures including lists, dictionaries, and dataframes',
                    'Automate repetitive tasks using Python scripts',
                    'Build basic data analysis pipelines using Pandas',
                    'Create visualizations to communicate insights'
                ],
                'modules': [
                    'Module 1: Python Fundamentals (Week 1-2)',
                    'Module 2: Data Structures and File Handling (Week 3-4)',
                    'Module 3: Data Analysis with Pandas (Week 5-6)',
                    'Module 4: Data Visualization (Week 7-8)'
                ],
                'assessment': [
                    'Weekly coding exercises (20%)',
                    'Mid-term project (30%)',
                    'Final capstone project (50%)'
                ],
                'implementation': {
                    'delivery_mode': 'Blended (online + practical sessions)',
                    'instructor_requirement': 'One instructor per 25 learners',
                    'facility_requirement': 'Computer lab with Python installed',
                    'estimated_cost': 'KES 25,000 - 35,000 per learner'
                }
            },
            'aws': {
                'title': 'Cloud Computing with AWS',
                'duration': 6,
                'level': 'Intermediate',
                'prerequisites': ['Basic IT knowledge', 'Understanding of networking concepts'],
                'learning_outcomes': [
                    'Design and deploy cloud infrastructure on AWS',
                    'Configure EC2, S3, and RDS services',
                    'Implement basic security controls',
                    'Monitor and optimize cloud costs',
                    'Troubleshoot common cloud issues'
                ],
                'modules': [
                    'Module 1: Cloud Computing Fundamentals (Week 1)',
                    'Module 2: AWS Core Services - EC2 and S3 (Week 2-3)',
                    'Module 3: Databases and Networking (Week 4-5)',
                    'Module 4: Security and Cost Management (Week 6)'
                ],
                'assessment': [
                    'Hands-on lab exercises (30%)',
                    'Cloud architecture project (30%)',
                    'Final practical exam (40%)'
                ],
                'implementation': {
                    'delivery_mode': 'Online with hands-on labs',
                    'instructor_requirement': 'AWS-certified instructor',
                    'facility_requirement': 'Internet-connected computers, AWS accounts',
                    'estimated_cost': 'KES 30,000 - 45,000 per learner'
                }
            },
            'docker': {
                'title': 'Containerization with Docker',
                'duration': 4,
                'level': 'Intermediate',
                'prerequisites': ['Linux basics', 'Command line experience'],
                'learning_outcomes': [
                    'Build and run Docker containers',
                    'Create Docker images using Dockerfiles',
                    'Manage multi-container applications with Docker Compose',
                    'Implement container networking and volumes',
                    'Apply container security best practices'
                ],
                'modules': [
                    'Module 1: Docker Basics (Week 1)',
                    'Module 2: Docker Images and Dockerfiles (Week 2)',
                    'Module 3: Docker Compose and Multi-container Apps (Week 3)',
                    'Module 4: Networking, Volumes, and Security (Week 4)'
                ],
                'assessment': [
                    'Lab exercises (25%)',
                    'Containerization project (35%)',
                    'Final technical assessment (40%)'
                ],
                'implementation': {
                    'delivery_mode': 'Hands-on lab-based',
                    'instructor_requirement': 'DevOps experienced instructor',
                    'facility_requirement': 'Computers with Docker installed',
                    'estimated_cost': 'KES 20,000 - 30,000 per learner'
                }
            },
            'kubernetes': {
                'title': 'Kubernetes Orchestration',
                'duration': 6,
                'level': 'Advanced',
                'prerequisites': ['Docker experience', 'YAML basics'],
                'learning_outcomes': [
                    'Deploy and manage applications on Kubernetes clusters',
                    'Configure Pods, Services, and Deployments',
                    'Implement rolling updates and rollbacks',
                    'Manage ConfigMaps and Secrets',
                    'Troubleshoot common Kubernetes issues'
                ],
                'modules': [
                    'Module 1: Kubernetes Architecture (Week 1)',
                    'Module 2: Pods, Services, and Deployments (Week 2-3)',
                    'Module 3: Configuration and Storage (Week 4-5)',
                    'Module 4: Troubleshooting and Best Practices (Week 6)'
                ],
                'assessment': [
                    'Weekly lab tasks (30%)',
                    'Cluster deployment project (30%)',
                    'Final practical exam (40%)'
                ],
                'implementation': {
                    'delivery_mode': 'Online with cluster access',
                    'instructor_requirement': 'Kubernetes certified instructor',
                    'facility_requirement': 'Access to Kubernetes cluster (Minikube or cloud)',
                    'estimated_cost': 'KES 35,000 - 50,000 per learner'
                }
            },
            'cybersecurity': {
                'title': 'Cybersecurity Fundamentals',
                'duration': 6,
                'level': 'Beginner to Intermediate',
                'prerequisites': ['Basic IT knowledge', 'Understanding of networks'],
                'learning_outcomes': [
                    'Identify common cyber threats and vulnerabilities',
                    'Implement basic security controls',
                    'Conduct security risk assessments',
                    'Respond to security incidents',
                    'Apply security best practices in daily operations'
                ],
                'modules': [
                    'Module 1: Cybersecurity Concepts (Week 1)',
                    'Module 2: Network Security (Week 2-3)',
                    'Module 3: Application and Data Security (Week 4-5)',
                    'Module 4: Incident Response and Governance (Week 6)'
                ],
                'assessment': [
                    'Weekly quizzes (20%)',
                    'Risk assessment project (30%)',
                    'Final examination (50%)'
                ],
                'implementation': {
                    'delivery_mode': 'Blended (theory + practical labs)',
                    'instructor_requirement': 'Security certified instructor',
                    'facility_requirement': 'Computer lab with security tools',
                    'estimated_cost': 'KES 25,000 - 40,000 per learner'
                }
            }
        }
    
    def get_template(self, skill: str) -> Optional[Dict]:
        """Get course template for a specific skill"""
        skill_lower = skill.lower()
        for key, template in self.course_templates.items():
            if key in skill_lower or skill_lower in key:
                return template
        return None
    
    def generate_course(self, skill: str, priority_tier: str, market_freq: int, 
                        gap_score: float) -> Dict:
        """
        Generate a complete course specification for a skill gap.
        
        Returns dictionary with all course details.
        """
        template = self.get_template(skill)
        
        if template:
            course = template.copy()
            # Customize based on priority and demand
            course['skill_gap'] = skill
            course['priority'] = priority_tier
            course['market_demand'] = market_freq
            course['gap_score'] = gap_score
            
            # Adjust duration based on priority
            if priority_tier == 'High' and course['duration'] > 4:
                # High priority courses can be accelerated
                course['duration'] = max(4, course['duration'] - 2)
                course['note'] = 'Accelerated due to high market demand'
        else:
            # Generic course template for unknown skills
            course = {
                'title': f'{skill.upper()} Professional Certificate',
                'duration': 6,
                'level': 'Intermediate',
                'prerequisites': ['Basic computer literacy', 'Relevant foundational knowledge'],
                'learning_outcomes': [
                    f'Master core {skill} concepts and techniques',
                    f'Apply {skill} to real-world industry problems',
                    f'Build practical projects demonstrating {skill} proficiency',
                    'Collaborate effectively in team-based technical environments',
                    'Prepare for industry certification exams'
                ],
                'modules': [
                    'Module 1: Foundations (Week 1-2)',
                    'Module 2: Core Techniques (Week 3-4)',
                    'Module 3: Advanced Applications (Week 5-6)'
                ],
                'assessment': [
                    'Practical assignments (30%)',
                    'Mid-term project (30%)',
                    'Final capstone project (40%)'
                ],
                'implementation': {
                    'delivery_mode': 'Blended learning',
                    'instructor_requirement': 'Qualified industry instructor',
                    'facility_requirement': 'Standard computer lab',
                    'estimated_cost': 'KES 20,000 - 35,000 per learner'
                },
                'skill_gap': skill,
                'priority': priority_tier,
                'market_demand': market_freq,
                'gap_score': gap_score
            }
        
        return course
    
    def generate_courses_from_prioritized_gaps(self, prioritized_gaps: pd.DataFrame, 
                                                max_courses: int = 8) -> List[Dict]:
        """
        Generate courses from prioritized gaps DataFrame.
        
        Parameters:
        - prioritized_gaps: DataFrame with columns (skill, priority_tier, market_frequency, priority_score)
        - max_courses: Maximum number of courses to generate
        """
        if prioritized_gaps is None or len(prioritized_gaps) == 0:
            return []
        
        courses = []
        for _, row in prioritized_gaps.head(max_courses).iterrows():
            # Get gap_score - try multiple possible column names
            gap_score_val = 0
            if 'gap_score' in row:
                gap_score_val = row['gap_score']
            elif 'priority_score' in row:
                gap_score_val = row['priority_score']
            
            course = self.generate_course(
                skill=row['skill'],
                priority_tier=row['priority_tier'],
                market_freq=row['market_frequency'],
                gap_score=gap_score_val
            )
            courses.append(course)
        
        self.courses = courses
        return courses
    
    def get_courses_dataframe(self) -> pd.DataFrame:
        """Convert generated courses to DataFrame for display"""
        if not self.courses:
            return pd.DataFrame()
        
        courses_data = []
        for c in self.courses:
            courses_data.append({
                'title': c.get('title', 'N/A'),
                'skill_gap': c.get('skill_gap', 'N/A'),
                'duration_weeks': c.get('duration', 'N/A'),
                'level': c.get('level', 'N/A'),
                'priority': c.get('priority', 'N/A'),
                'market_demand': c.get('market_demand', 0),
                'gap_score': c.get('gap_score', 0),
                'learning_outcomes': '\n'.join(c.get('learning_outcomes', [])),
                'modules': '\n'.join(c.get('modules', [])),
                'assessment': '\n'.join(c.get('assessment', [])),
                'delivery_mode': c.get('implementation', {}).get('delivery_mode', 'N/A'),
                'estimated_cost': c.get('implementation', {}).get('estimated_cost', 'N/A')
            })
        
        return pd.DataFrame(courses_data)
    
    def export_to_json(self, filepath: str = None) -> str:
        """Export courses to JSON format"""
        if filepath:
            import json
            with open(filepath, 'w') as f:
                json.dump(self.courses, f, indent=2)
            return filepath
        return json.dumps(self.courses, indent=2)
    
    def get_summary(self) -> Dict:
        """Get summary of generated courses"""
        if not self.courses:
            return {'total_courses': 0}
        
        priorities = [c.get('priority', 'Unknown') for c in self.courses]
        return {
            'total_courses': len(self.courses),
            'high_priority_courses': priorities.count('High'),
            'medium_priority_courses': priorities.count('Medium'),
            'low_priority_courses': priorities.count('Low'),
            'total_duration_weeks': sum(c.get('duration', 0) for c in self.courses),
            'skills_covered': [c.get('skill_gap', '') for c in self.courses]
        }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":
    print("Testing Course Generator...")
    
    # Sample prioritized gaps
    sample_gaps = pd.DataFrame({
        'skill': ['aws', 'kubernetes', 'docker', 'cybersecurity', 'python', 'sql', 'tensorflow'],
        'priority_tier': ['High', 'High', 'High', 'Medium', 'Medium', 'Low', 'Low'],
        'market_frequency': [38, 28, 32, 15, 45, 25, 22],
        'gap_score': [0.78, 0.76, 0.75, 0.66, 0.45, 0.33, 0.31]
    })
    
    print("\n1. Sample prioritized gaps:")
    print(sample_gaps)
    
    # Initialize generator
    generator = CourseGenerator()
    
    # Generate courses
    print("\n2. Generating courses...")
    courses = generator.generate_courses_from_prioritized_gaps(sample_gaps, max_courses=5)
    
    print(f"Generated {len(courses)} courses")
    
    # Display first course
    if courses:
        print("\n3. Sample course details:")
        first = courses[0]
        print(f"   Title: {first.get('title')}")
        print(f"   Duration: {first.get('duration')} weeks")
        print(f"   Priority: {first.get('priority')}")
        print(f"   Learning outcomes:")
        for outcome in first.get('learning_outcomes', [])[:3]:
            print(f"     - {outcome}")
    
    # Get DataFrame
    print("\n4. Courses DataFrame:")
    df = generator.get_courses_dataframe()
    print(df[['title', 'duration_weeks', 'priority', 'market_demand']])
    
    # Get summary
    print("\n5. Summary:")
    summary = generator.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\nCourse Generator ready!")