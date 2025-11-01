"""
Supabase Storage client for handling file uploads and downloads.
"""
import os
import uuid
from typing import Optional, BinaryIO
from django.conf import settings
from supabase import create_client, Client


class SupabaseStorageClient:
    """Helper class for Supabase Storage operations."""
    
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role for server-side operations
        self.bucket = settings.SUPABASE_STORAGE_BUCKET
        
        if not all([self.url, self.key, self.bucket]):
            raise ValueError("Supabase configuration is incomplete. Check your environment variables.")
        
        self.client: Client = create_client(self.url, self.key)
    
    def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        folder: str = "scripts",
        content_type: str = "application/octet-stream"
    ) -> tuple[bool, str]:
        """
        Upload a file to Supabase Storage.
        
        Args:
            file: File-like object to upload
            filename: Original filename
            folder: Storage folder/path
            content_type: MIME type of the file
            
        Returns:
            tuple: (success: bool, url_or_error: str)
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            storage_path = f"{folder}/{unique_filename}"
            
            # Upload file
            response = self.client.storage.from_(self.bucket).upload(
                path=storage_path,
                file=file,
                file_options={
                    "content-type": content_type,
                    "upsert": False
                }
            )
            
            if response.get('error'):
                return False, f"Upload failed: {response['error']}"
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket).get_public_url(storage_path)
            
            return True, public_url
            
        except Exception as e:
            return False, f"Upload error: {str(e)}"
    
    def delete_file(self, file_path: str) -> tuple[bool, str]:
        """
        Delete a file from Supabase Storage.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            response = self.client.storage.from_(self.bucket).remove([file_path])
            
            if response.get('error'):
                return False, f"Delete failed: {response['error']}"
            
            return True, "File deleted successfully"
            
        except Exception as e:
            return False, f"Delete error: {str(e)}"
    
    def get_public_url(self, file_path: str) -> str:
        """
        Get the public URL for a file.
        
        Args:
            file_path: Path to the file in storage
            
        Returns:
            Public URL string
        """
        return self.client.storage.from_(self.bucket).get_public_url(file_path)
    
    def create_signed_url(self, file_path: str, expires_in: int = 3600) -> tuple[bool, str]:
        """
        Create a signed URL for private file access.
        
        Args:
            file_path: Path to the file in storage
            expires_in: Expiration time in seconds (default: 1 hour)
            
        Returns:
            tuple: (success: bool, url_or_error: str)
        """
        try:
            response = self.client.storage.from_(self.bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            if response.get('error'):
                return False, f"Signed URL creation failed: {response['error']}"
            
            return True, response.get('signedURL', '')
            
        except Exception as e:
            return False, f"Signed URL error: {str(e)}"


# Global instance
storage_client = SupabaseStorageClient() if all([
    settings.SUPABASE_URL, 
    settings.SUPABASE_SERVICE_ROLE_KEY, 
    settings.SUPABASE_STORAGE_BUCKET
]) else None