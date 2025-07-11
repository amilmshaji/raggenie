# src/endpoints/chat.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import app.schemas.common as resp_schemas
from app.schemas import llmchat as schemas
from app.utils.database import get_db
from app.services import llmchat as svc
import app.api.v1.commons as commons

chat_router = APIRouter()

# Create a new chat
@chat_router.post("/create", response_model=resp_schemas.CommonResponse)
async def create_chat(chat: schemas.ChatHistoryCreate, db: Session = Depends(get_db)):

    """
    Creates a new chat record in the database.

    Args:
        chat (ChatHistoryCreate): The data for the new chat entry.
        db (Session): Database session dependency.

    Returns:
        CommonResponse: A response indicating success or failure of the chat creation process.
    """

    result, error = svc.create_chat(chat, db)

    if error:
        return commons.is_error_response("DB Error", result, {"chat": {}})

    return resp_schemas.CommonResponse(
        status=True,
        status_code=201,
        data={"chat": result},
        message="Chat created successfully",
        error=None
    )

# Create feedback for a chat
@chat_router.post("/feedback/create", response_model=resp_schemas.CommonResponse)
def create_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):

    """
    Creates feedback for an existing chat record.

    Args:
        feedback (FeedbackCreate): The feedback data to be added to the chat.
        db (Session): Database session dependency.

    Returns:
        CommonResponse: A response indicating success or failure of the feedback creation process.
    """

    result, error = svc.create_feedback(feedback, db)

    if error:
        return commons.is_error_response("DB Error", result, {"chat": {}})

    if not result:
        return commons.is_none_reponse("Chat Not Found", {"chat": {}})

    return resp_schemas.CommonResponse(
        status=True,
        status_code=200,
        data={"chat": result},
        message="Feedback updated successfully",
        error=None
    )

# List the primary chat based on context
@chat_router.get("/list/context/all/{env_id}/{user_id}", response_model=resp_schemas.CommonResponse)
async def list_chat_by_context(env_id: int, user_id: int,  db: Session = Depends(get_db)):

    """
    Retrieves all the primary chats based on context from the database.

    Args:
        db (Session): Database session dependency.

    Returns:
        CommonResponse: A response containing either the list of primary chats or an error message.
    """

    result, error = svc.list_chats_by_context(env_id, user_id, db)

    if error:
        return commons.is_error_response("DB Error", error, {"chats": []})

    if not result:
        return commons.is_none_reponse("Context Not found", {"chats": []})


    return resp_schemas.CommonResponse(
        status=True,
        status_code=200,
        data={"chats": result},
        message="Primary chats found",
        error=None
    )



# Get paginated chats by context ID
@chat_router.get("/get/{context_id}", response_model=resp_schemas.CommonResponse)
async def get_paginated_chats_by_context(
    context_id: str,    
    offset: int = Query(0, description="Offset for pagination"),
    limit: int = Query(10, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated chat records by context ID from the database.

    Args:
        context_id (str): The ID of the context to retrieve chats for.
        offset (int): The number of chats to skip (for pagination).
        limit (int): The maximum number of chats to retrieve.
        db (Session): Database session dependency.

    Returns:
        CommonResponse: A response with chat data or an error message.
    """

    result, error = svc.list_paginated_chats_by_context_id(context_id, offset, limit, db)

    if error:
        return commons.is_error_response("DB Error", error, {"chats": []})

    if not result:
        return commons.is_none_reponse("No chats found", {"chats": []})

    return resp_schemas.CommonResponse(
        status=True,
        status_code=200,
        data={"chats": result},
        message="Chats retrieved successfully",
        error=None
    )
