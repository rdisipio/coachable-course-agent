#!/usr/bin/env python3
"""
Upload updated ChromaDB archive to HuggingFace datasets repository.
"""

import os
import tarfile
import json
from huggingface_hub import HfApi, login
from pathlib import Path

def create_courses_tarball():
    """Create a compressed tarball of the courses ChromaDB."""
    chroma_dir = "data/courses_chroma"
    output_file = "data/courses_chroma.tar.gz"
    
    if not os.path.exists(chroma_dir):
        print(f"❌ Error: {chroma_dir} not found!")
        return False
    
    print(f"📦 Creating tarball from {chroma_dir}...")
    
    try:
        with tarfile.open(output_file, "w:gz") as tar:
            tar.add(chroma_dir, arcname="courses_chroma")
        
        file_size = os.path.getsize(output_file)
        print(f"✅ Created {output_file} ({file_size / 1024 / 1024:.1f} MB)")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tarball: {e}")
        return False

def get_catalog_stats():
    """Get current catalog statistics for commit message."""
    try:
        with open("data/course_catalog_esco.json", 'r') as f:
            catalog = json.load(f)
        
        total_courses = len(catalog['courses'])
        total_skills = sum(len(course.get('skills', [])) for course in catalog['courses'])
        
        cleanup_stats = catalog.get('metadata', {}).get('cleanup_stats', {})
        mock_courses_removed = cleanup_stats.get('mock_courses_removed', 0)
        
        return {
            'total_courses': total_courses,
            'total_skills': total_skills,
            'mock_courses_removed': mock_courses_removed
        }
    except Exception as e:
        print(f"❌ Could not read catalog stats: {e}")
        return {
            'total_courses': 'unknown',
            'total_skills': 'unknown', 
            'mock_courses_removed': 'unknown'
        }

def upload_courses_chroma():
    """Upload the updated courses_chroma.tar.gz to HuggingFace datasets repo."""
    
    # Repository details
    repo_id = "rdisipio/esco-skills"
    repo_type = "dataset"
    
    # File to upload
    local_file = "data/courses_chroma.tar.gz"
    repo_file = "courses_chroma.tar.gz"
    
    # Get catalog statistics
    stats = get_catalog_stats()
    
    # Create the tarball first
    print("🔧 Step 1: Creating ChromaDB tarball...")
    if not create_courses_tarball():
        return False
    
    # Check if file exists
    if not os.path.exists(local_file):
        print(f"❌ Error: {local_file} not found after creation!")
        return False
    
    # Get file size
    file_size = os.path.getsize(local_file)
    print(f"📦 Step 2: Uploading {local_file} ({file_size / 1024 / 1024:.1f} MB) to {repo_id}")
    
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
        
        # Create dynamic commit message
        commit_msg = f"Update courses_chroma.tar.gz with cleaned dataset ({stats['total_courses']} courses, {stats['total_skills']} skills"
        if stats['mock_courses_removed'] != 'unknown' and stats['mock_courses_removed'] > 0:
            commit_msg += f", removed {stats['mock_courses_removed']} mock courses"
        commit_msg += ")"
        
        # Upload the file directly
        print(f"🚀 Step 3: Starting upload...")
        print(f"📝 Commit message: {commit_msg}")
        result = api.upload_file(
            path_or_fileobj=local_file,
            path_in_repo=repo_file,
            repo_id=repo_id,
            repo_type=repo_type,
            commit_message=commit_msg
        )
        
        print(f"✅ Successfully uploaded to: {result}")
        print(f"🌐 View at: https://huggingface.co/datasets/{repo_id}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Creating and uploading updated ChromaDB to HuggingFace datasets repository...")
    
    # Get current stats for display
    stats = get_catalog_stats()
    print(f"📊 Current catalog: {stats['total_courses']} courses, {stats['total_skills']} skills")
    if stats['mock_courses_removed'] != 'unknown' and stats['mock_courses_removed'] > 0:
        print(f"🧹 Cleanup: {stats['mock_courses_removed']} mock courses removed")
    
    success = upload_courses_chroma()
    
    if success:
        print("\n🎉 Upload complete!")
        print("📋 Next steps:")
        print("   1. Verify the file was uploaded correctly")
        print("   2. Test the app to ensure it downloads the new archive")
        print(f"   3. The app will now use the updated {stats['total_courses']}-course dataset!")
    else:
        print("\n💥 Upload failed. Please check your credentials and try again.")
