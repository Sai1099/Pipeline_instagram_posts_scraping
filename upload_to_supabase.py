#!/usr/bin/env python3
"""
Script to upload scraped Instagram content to Supabase Storage
"""

import os
import json
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client
import mimetypes

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("ERROR: Missing Supabase credentials")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# Configuration
BUCKET_NAME = "instagramscrapingdata"
DOWNLOADS_DIR = Path("downloads")
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.webp', '.webm'}

def get_file_info(file_path):
    """Get file information for upload"""
    stat = file_path.stat()
    mime_type, _ = mimetypes.guess_type(str(file_path))
    
    return {
        'size': stat.st_size,
        'mime_type': mime_type or 'application/octet-stream',
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
    }

def upload_file_to_supabase(file_path, remote_path):
    """Upload a single file to Supabase Storage"""
    try:
        file_info = get_file_info(file_path)
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Upload to Supabase Storage
        response = supabase.storage.from_(BUCKET_NAME).upload(
            remote_path,
            file_content,
            file_options={
                'content-type': file_info['mime_type'],
                'cache-control': '3600'
            }
        )
        
        if response.status_code == 200:
            # Get public URL
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(remote_path)
            print(f"✅ Uploaded: {file_path.name} -> {public_url}")
            return public_url
        else:
            print(f"❌ Failed to upload {file_path.name}: {response}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading {file_path.name}: {str(e)}")
        return None

def create_upload_log(uploaded_files):
    """Create a log of uploaded files"""
    log_data = {
        'upload_date': datetime.now().isoformat(),
        'total_files': len(uploaded_files),
        'files': uploaded_files
    }
    
    log_filename = f"upload_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path = DOWNLOADS_DIR / log_filename
    
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"📋 Upload log created: {log_path}")
    return log_path

def main():
    """Main function to upload all files"""
    if not DOWNLOADS_DIR.exists():
        print(f"❌ Downloads directory not found: {DOWNLOADS_DIR}")
        return
    
    print(f"🚀 Starting upload to Supabase bucket: {BUCKET_NAME}")
    print(f"📁 Scanning directory: {DOWNLOADS_DIR}")
    
    uploaded_files = []
    total_files = 0
    successful_uploads = 0
    
    # Get today's date for organizing files
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Walk through all files in downloads directory
    for file_path in DOWNLOADS_DIR.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            total_files += 1
            
            # Create remote path: organized by date and original structure
            relative_path = file_path.relative_to(DOWNLOADS_DIR)
            remote_path = f"{today}/{relative_path}"
            
            # Upload file
            public_url = upload_file_to_supabase(file_path, remote_path)
            
            if public_url:
                successful_uploads += 1
                uploaded_files.append({
                    'local_path': str(file_path),
                    'remote_path': remote_path,
                    'public_url': public_url,
                    'file_size': file_path.stat().st_size,
                    'upload_time': datetime.now().isoformat()
                })
    
    # Create upload log
    if uploaded_files:
        create_upload_log(uploaded_files)
    
    print(f"\n📊 Upload Summary:")
    print(f"   Total files found: {total_files}")
    print(f"   Successful uploads: {successful_uploads}")
    print(f"   Failed uploads: {total_files - successful_uploads}")
    
    if successful_uploads > 0:
        print(f"\n🔗 Files are now available at:")
        print(f"   https://zfmhkdgxtqakljhwoblk.supabase.co/storage/v1/object/public/{BUCKET_NAME}/{today}/")

if __name__ == "__main__":
    main()