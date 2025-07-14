
from fastapi import APIRouter, Depends, File, HTTPException, status, Query, BackgroundTasks, UploadFile
from sqlalchemy.orm import Session
from app.schemas.feedback import ChatFeedbackUpdate
from app.utils.database import get_db
from loguru import logger

feedback = APIRouter()


