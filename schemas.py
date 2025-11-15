"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (you can keep these in your DB for testing):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App-specific schema
# --------------------------------------------------
class Book(BaseModel):
    """
    Books you upload so people can read and listen to an audio summary.
    Collection name: "book" (lowercase of class name)
    """
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    genre: str = Field(..., description="Primary genre/category")
    description: Optional[str] = Field(None, description="Short description or blurb")
    cover_url: Optional[HttpUrl] = Field(None, description="Image URL for the cover")
    content: Optional[str] = Field(None, description="Readable text content or excerpt")
    audio_summary_url: Optional[HttpUrl] = Field(None, description="Direct URL to the audio summary (mp3, wav, etc.)")
    tags: Optional[List[str]] = Field(default=None, description="Additional tags for search")
