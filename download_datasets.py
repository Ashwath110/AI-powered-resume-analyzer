"""
Dataset Downloader for AI-Powered Resume Analyzer
Downloads required datasets from Kaggle
"""

import os
import json
from pathlib import Path

def setup_kaggle_credentials(username, api_key):
    """
    Set up Kaggle API credentials
    """
    # Create .kaggle directory in user home
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_dir.mkdir(exist_ok=True)
    
    # Create kaggle.json file with username and key
    kaggle_json = {
        "username": username,
        "key": api_key
    }
    
    # Create kaggle.json file
    kaggle_json_path = kaggle_dir / 'kaggle.json'
    with open(kaggle_json_path, 'w') as f:
        json.dump(kaggle_json, f)
    
    # Set proper permissions (read/write for owner only)
    try:
        os.chmod(kaggle_json_path, 0o600)
    except:
        pass  # Windows doesn't support chmod the same way
    
    print(f"✓ Kaggle credentials set up at {kaggle_json_path}")
    
    # Set environment variables for Kaggle API
    os.environ['KAGGLE_USERNAME'] = username
    os.environ['KAGGLE_KEY'] = api_key
    
    return True

def create_directories():
    """
    Create necessary directories for datasets
    """
    dirs = [
        'datasets',
        'datasets/resumes',
        'datasets/jobs',
        'datasets/skills'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def download_dataset(dataset_name, output_dir):
    """
    Download a dataset from Kaggle using the API
    """
    print(f"\n📥 Downloading {dataset_name}...")
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Initialize API
        api = KaggleApi()
        api.authenticate()
        
        # Download and unzip dataset
        api.dataset_download_files(dataset_name, path=output_dir, unzip=True)
        
        print(f"✓ Successfully downloaded {dataset_name}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {dataset_name}: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("AI-Powered Resume Analyzer - Dataset Downloader")
    print("=" * 60)
    
    # API Key format: KGAT_<actual_key>
    # For Kaggle, we need username and key separately
    # Common Kaggle usernames that share datasets
    username = "gauravduttakiit"  # Or the actual username from the dataset
    api_key = "997c5c50ebfa4cf3ad88656223966bc4"  # Extracted from KGAT_...
    
    print("\n📋 Step 1: Setting up Kaggle credentials...")
    setup_kaggle_credentials(username, api_key)
    
    print("\n📋 Step 2: Creating directories...")
    create_directories()
    
    print("\n📋 Step 3: Downloading datasets...")
    
    # Common resume datasets on Kaggle
    datasets = [
        {
            'name': 'gauravduttakiit/resume-dataset',
            'output': 'datasets/resumes',
            'description': 'Resume Dataset'
        },
        # You can add more datasets here
    ]
    
    success_count = 0
    for dataset in datasets:
        print(f"\nDataset: {dataset['description']}")
        if download_dataset(dataset['name'], dataset['output']):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"✓ Download complete! {success_count}/{len(datasets)} datasets downloaded successfully")
    print("=" * 60)
    
    # List downloaded files
    print("\n📁 Downloaded files:")
    for root, dirs, files in os.walk('datasets'):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()
