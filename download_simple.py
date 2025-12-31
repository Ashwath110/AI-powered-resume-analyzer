"""
Simple Dataset Downloader - Uses publicly available datasets
"""

import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

def create_directories():
    """Create necessary directories"""
    dirs = ['datasets', 'datasets/resumes', 'datasets/jobs', 'datasets/skills']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def download_resume_dataset():
    """Download resume dataset from Kaggle"""
    print("\n📥 Initializing Kaggle API...")
    
    try:
        # Initialize Kaggle API (reads from ~/.kaggle/kaggle.json)
        api = KaggleApi()
        api.authenticate()
        print("✓ Kaggle API authenticated successfully")
        
        # Popular resume datasets to try
        datasets_to_try = [
            'gauravduttakiit/resume-dataset',
            'snehaanbhawal/resume-dataset',
            'dhainjeamita/updated-resume-dataset'
        ]
        
        print("\n📋 Searching for available resume datasets...")
        
        for dataset_name in datasets_to_try:
            try:
                print(f"\n📥 Attempting to download: {dataset_name}")
                api.dataset_download_files(
                    dataset_name, 
                    path='datasets/resumes', 
                    unzip=True
                )
                print(f"✓ Successfully downloaded {dataset_name}")
                return True
            except Exception as e:
                print(f"  ✗ {dataset_name} not available: {str(e)}")
                continue
        
        print("\n⚠ Could not download from pre-configured datasets.")
        print("  Searching for public resume datasets...")
        
        # Search for resume datasets
        datasets = api.dataset_list(search='resume')
        if datasets:
            print(f"\nFound {len(datasets)} resume-related datasets:")
            for i, ds in enumerate(datasets[:5], 1):
                print(f"  {i}. {ds.ref}")
            
            # Try downloading the first one
            first_dataset = str(datasets[0].ref)
            print(f"\n📥 Downloading: {first_dataset}")
            api.dataset_download_files(first_dataset, path='datasets/resumes', unzip=True)
            print(f"✓ Successfully downloaded {first_dataset}")
            return True
        else:
            print("✗ No resume datasets found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("\n⚠ Make sure your Kaggle API credentials are set up correctly.")
        print("  Create a file at: C:\\Users\\Lapash_110\\.kaggle\\kaggle.json")
        print("  With content: {\"username\": \"your_username\", \"key\": \"your_api_key\"}")
        return False

def list_downloaded_files():
    """List all downloaded files"""
    print("\n📁 Downloaded files:")
    file_count = 0
    for root, dirs, files in os.walk('datasets'):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"  - {file_path} ({file_size:.2f} KB)")
            file_count += 1
    
    if file_count == 0:
        print("  (No files downloaded yet)")
    else:
        print(f"\n✓ Total files: {file_count}")

def main():
    print("=" * 70)
    print("AI-Powered Resume Analyzer - Dataset Downloader")
    print("=" * 70)
    
    print("\n📋 Step 1: Creating directories...")
    create_directories()
    
    print("\n📋 Step 2: Downloading datasets...")
    success = download_resume_dataset()
    
    print("\n" + "=" * 70)
    if success:
        print("✓ Dataset download complete!")
    else:
        print("⚠ Dataset download failed - check API credentials")
    print("=" * 70)
    
    list_downloaded_files()

if __name__ == "__main__":
    main()
