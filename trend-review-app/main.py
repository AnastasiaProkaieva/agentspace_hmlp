import uuid
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from pydantic import BaseModel
from typing import Literal

# Initialize FastAPI app
app = FastAPI(title="Story Draft Review App")

# Mount the 'static' directory to serve files like images
# This line should be added right after you create the app
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Firestore client
# On Cloud Run, this will automatically use the runtime service account.
db = firestore.Client()

# Pydantic Models for request body validation
class StoryOutline(BaseModel):
    outline: str

class ReviewDecision(BaseModel):
    decision: Literal['approved', 'disapproved']

# Setup for rendering HTML templates
templates = Jinja2Templates(directory="templates")

@app.post("/reviews")
async def create_review(story_outline: StoryOutline):
    """
    Endpoint for the ADK agent to submit a new story outline for review.
    Creates a document in Firestore with a 'pending' status.
    """
    review_id = str(uuid.uuid4())
    review_data = {
        "outline": story_outline.outline,
        "status": "pending",
        "decision": None,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("reviews").document(review_id).set(review_data)

    # This assumes the app is running on Cloud Run and we can construct the URL
    # The base URL will need to be configured in the agent.
    # For local testing, you might need a different base URL.
    # Note: In a real app, the base URL should come from an env var.
    return {"review_id": review_id}

@app.get("/reviews/{review_id}/view", response_class=HTMLResponse)
async def get_review_page(request: Request, review_id: str):
    """
    Serves the HTML page for a human to review the draft.
    """
    doc_ref = db.collection("reviews").document(review_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")

    return templates.TemplateResponse(
        "review.html", 
        {"request": request, "review_id": review_id, "data": doc.to_dict()}
    )

@app.post("/reviews/{review_id}/decide", response_class=HTMLResponse)
async def decide_on_review(
    review_id: str,
    decision: str = Form(...),
    outline: str = Form(...),
    comment: str = Form(...)
):
    """
    Endpoint called by the HTML form. Updates the Firestore document with the
    decision, the (potentially edited) outline, and any comments.
    """
    doc_ref = db.collection("reviews").document(review_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")

    if decision not in ["approved", "disapproved"]:
        raise HTTPException(status_code=400, detail="Invalid decision")

    # If disapproved, a comment is mandatory (enforced by frontend, but good to check here too)
    if decision == "disapproved" and not comment.strip():
         raise HTTPException(status_code=400, detail="Comment is required for disapproval.")

    doc_ref.update({
        "status": decision,
        "decision": decision,
        "outline": outline,  # Save the potentially edited outline
        "comment": comment,  # Save the comment
        "reviewed_at": firestore.SERVER_TIMESTAMP
    })

    return HTMLResponse(content=f"<h1>Thank you!</h1><p>Your decision ('{decision}') has been recorded.</p>")

@app.get("/reviews/{review_id}/status")
async def get_review_status(review_id: str):
    """
    A simple endpoint for the ADK agent to poll the status of the review.
    Now returns the full review data.
    """
    doc_ref = db.collection("reviews").document(review_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Review not found")

    # Return the entire document data so the agent can access status, comments, and the final outline
    return doc.to_dict()


@app.get("/admin/clear-all-reviews")
async def clear_all_reviews():
    """
    Deletes all documents in the 'reviews' collection.

    USE WITH CAUTION. This is for demonstration purposes.
    """
    reviews_collection = db.collection("reviews")
    docs = reviews_collection.stream()
    deleted_count = 0
    for doc in docs:
        doc.reference.delete()
        deleted_count += 1
    return {"message": f"Successfully deleted {deleted_count} reviews."}


@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Story Review App is running.</h1>"