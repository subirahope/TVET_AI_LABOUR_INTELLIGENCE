print("Script started...")

try:
    from src.data_loader import DataLoader
    print("✅ Import successful")
    
    loader = DataLoader()
    print("✅ DataLoader created")
    
    df = loader.generate_sample_job_data()
    print(f"✅ Generated {len(df)} jobs")
    
    print(df.head())
    
except Exception as e:
    print(f"❌ Error: {e}")