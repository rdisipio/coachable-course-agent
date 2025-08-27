#!/usr/bin/env python3
"""
Upload updated ChromaDB archive to HuggingFace datasets repository.
"""

import os
from huggingface_hub import HfApi, login
from pathlib import Path

def upload_courses_chroma():
    """Upload the updated courses_chroma.tar.gz to HuggingFace datasets repo."""
    
    # Repository details
    repo_id = "rdisipio/esco-skills"
    repo_type = "dataset"
    
    # File to upload
    local_file = "data/courses_chroma.tar.gz"
    repo_file = "courses_chroma.tar.gz"
    
    # Check if file exists
    if not os.path.exists(local_file):
        print(f"❌ Error: {local_file} not found!")
        return False
    
    # Get file size
    file_size = os.path.getsize(local_file)
    print(f"📦 Uploading {local_file} ({file_size / 1024 / 1024:.1f} MB) to {repo_id}")
    
    try:
        # Initialize HF API
        api = HfApi()
        
        # Check if we're already logged in, if not, prompt for login
        try:
            whoami = api.whoami()
            print(f"✅ Logged in as: {whoami['name']}")
        except Exception:
            print("🔐 Please login to HuggingFace Hub...")
            login()
        
        # Upload the file directly
        print(f"🚀 Starting direct upload...")
        result = api.upload_file(
            path_or_fileobj=local_file,
            path_in_repo=repo_file,
            repo_id=repo_id,
            repo_type=repo_type,
            commit_message="Update courses_chroma.tar.gz with cleaned dataset (366 courses, 4262 skills)"
        )
        
        print(f"✅ Successfully uploaded to: {result}")
        print(f"🌐 View at: https://huggingface.co/datasets/{repo_id}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Uploading updated ChromaDB to HuggingFace datasets repository...")
    success = upload_courses_chroma()
    
    if success:
        print("\n🎉 Upload complete!")
        print("📋 Next steps:")
        print("   1. Verify the file was uploaded correctly")
        print("   2. Test the app to ensure it downloads the new archive")
        print("   3. The app will now use the updated 366-course dataset!")
    else:
        print("\n💥 Upload failed. Please check your credentials and try again.")
