import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Book

app = FastAPI(title="Books + Audio Summaries API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Books API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ------------- Books Endpoints -------------
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    content: Optional[str] = None
    audio_summary_url: Optional[str] = None
    tags: Optional[List[str]] = None

@app.post("/api/books")
def create_book(payload: BookCreate):
    try:
        book = Book(**payload.model_dump())
        inserted_id = create_document("book", book)
        return {"id": inserted_id, "message": "Book created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/books")
def list_books(genre: Optional[str] = None, q: Optional[str] = None):
    try:
        filter_dict = {}
        if genre:
            filter_dict["genre"] = genre
        if q:
            # Basic search on title/author/tags
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"author": {"$regex": q, "$options": "i"}},
                {"tags": {"$elemMatch": {"$regex": q, "$options": "i"}}},
            ]
        docs = get_documents("book", filter_dict=filter_dict)
        # Convert ObjectId to string for _id
        for d in docs:
            d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/{book_id}")
def get_book(book_id: str):
    try:
        from bson import ObjectId
        doc = db["book"].find_one({"_id": ObjectId(book_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Book not found")
        doc["id"] = str(doc.pop("_id"))
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Minimal update endpoint for future use (not used by frontend yet)
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    content: Optional[str] = None
    audio_summary_url: Optional[str] = None
    tags: Optional[List[str]] = None

@app.patch("/api/books/{book_id}")
def update_book(book_id: str, payload: BookUpdate):
    try:
        from bson import ObjectId
        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not updates:
            return {"message": "Nothing to update"}
        updates["updated_at"] = __import__("datetime").datetime.utcnow()
        result = db["book"].update_one({"_id": ObjectId(book_id)}, {"$set": updates})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"message": "Book updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
