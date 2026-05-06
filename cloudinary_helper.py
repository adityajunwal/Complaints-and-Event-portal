import os
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_image(file) -> str:
    """Upload a file-like object to Cloudinary and return its public URL."""
    try:
        result = cloudinary.uploader.upload(file, timeout=60)
        return result["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
