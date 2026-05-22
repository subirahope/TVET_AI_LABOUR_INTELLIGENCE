"""
Test script for DataLoader module
Run: python test_loader.py
"""

from src.data_loader import DataLoader

# Initialize
loader = DataLoader()

# Generate sample data
print("Generating sample job data...")
df = loader.generate_sample_job_data()
print(f"Created {len(df)} sample job postings")

# Show sample
print("\nSample job posting:")
print(df.iloc[0]['title'])
print(df.iloc[0]['description'][:100] + "...")

# Get summary
summary = loader.get_data_summary()
print(f"\nData Summary: {summary}")