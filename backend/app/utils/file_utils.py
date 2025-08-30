"""Utility functions for handling file uploads and storage."""
import hashlib
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional, Tuple, Union

from fastapi import UploadFile

from app.core.config import settings


def get_file_hash(file_data: bytes) -> str:
    """
    Generate a SHA-256 hash for the given file data.
    
    Args:
        file_data: Binary content of the file
        
    Returns:
        Hex digest of the file hash
    """
    return hashlib.sha256(file_data).hexdigest()


def get_safe_filename(filename: str) -> str:
    """
    Convert a filename to a safe string that can be used as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename with special characters replaced
    """
    # Replace or remove characters that are not safe in filenames
    keep_chars = (' ', '.', '_', '-')
    safe_name = "".join(
        c if c.isalnum() or c in keep_chars else "_" 
        for c in filename
    ).rstrip()
    return safe_name


def ensure_upload_dir() -> Path:
    """
    Ensure the upload directory exists and return its path.
    
    Returns:
        Path to the upload directory
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def save_upload_file(
    upload_file: UploadFile, 
    destination: Union[str, Path],
    max_size: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Save an uploaded file to the specified destination.
    
    Args:
        upload_file: The uploaded file
        destination: Path where to save the file
        max_size: Maximum file size in bytes (optional)
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Ensure the destination directory exists
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check file size if max_size is provided
        if max_size is not None:
            # Read the file content to get its size
            content = await upload_file.read()
            if len(content) > max_size:
                return False, f"File size exceeds maximum allowed size of {max_size} bytes"
            
            # Write the content to the destination
            with open(dest_path, "wb") as buffer:
                buffer.write(content)
        else:
            # Stream the file in chunks for large files
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
        
        return True, "File uploaded successfully"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


def delete_file(file_path: Union[str, Path]) -> bool:
    """
    Delete a file if it exists.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if the file was deleted, False otherwise
    """
    try:
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception:
        return False


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename, converted to lowercase.
    
    Args:
        filename: The filename
        
    Returns:
        The file extension (without the dot), or an empty string if no extension
    """
    return Path(filename).suffix.lower().lstrip('.')


def is_valid_file_type(filename: str, allowed_extensions: list[str]) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: The filename to check
        allowed_extensions: List of allowed file extensions (without leading dots)
        
    Returns:
        True if the file has an allowed extension, False otherwise
    """
    if not filename:
        return False
    
    file_ext = get_file_extension(filename)
    return file_ext in {ext.lower() for ext in allowed_extensions}
