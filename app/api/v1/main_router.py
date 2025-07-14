from fastapi.responses import FileResponse
from app.providers.cache_manager import cache_manager
from fastapi import APIRouter, Depends, File, HTTPException, status, Query, BackgroundTasks, UploadFile
from fastapi.encoders import jsonable_encoder
from app.models.request import Chat, FeedbackCorrectionRequest
from starlette.requests import Request
from loguru import logger
from app.schemas import llmchat as schemas
from app.api.v1 import llmchat
from app.api.v1 import connector
from sqlalchemy.orm import Session
from app.utils.database import get_db
import time
import uuid

MainRouter = APIRouter()

async def save_data(chat_id, context_id, content, out, chat_context, user_id,config_id, env_id, db):
    resp = await llmchat.create_chat(
        schemas.ChatHistoryCreate(
            chat_id = chat_id,
            chat_context_id=context_id,
            chat_query=content,
            chat_answer= jsonable_encoder(out),
            chat_context = jsonable_encoder({}),
            chat_summary=out.get("summary", content),
            user_id=user_id,
            configuration_id=config_id,
            environment_id=env_id
        ),
        db
    )
    logger.info(f"saving chat to database")
    if resp.status:
        chat_id = resp.data["chat"].chat_id

@MainRouter.post("/query", status_code=status.HTTP_201_CREATED)

async def qna(
    query: Chat,
    request: Request,
    background_tasks: BackgroundTasks,
    context_id: str = Query(..., alias="contextId"),
    config_id: str = Query(..., alias="configId"),
    env_id: str = Query(..., alias="envId"),
    user_id: int = Query(..., alias="userId"),
    db: Session = Depends(get_db),
):

    """
    Handles user queries and invokes the chain to get an answer from the LLM.

    Args:
        query (Chat): User query as a Chat model.
        request (Request): FastAPI request object containing context and app-level dependencies.
        background_tasks (BackgroundTasks): Background task for asynchronous logging.
        db (Session): Database session dependency.

    Returns:
        dict: Response containing the answer to the user's query and the original query text.
    """
    
    logger.info(f"{context_id} - {config_id} - query: {query.content}")
    cached_data = cache_manager.get(int(config_id))
    if not cached_data:
        logger.info("configuration was not found in the cache")
        response = await connector.create_yaml(request, int(config_id), db, False)
        if response['success'] == True:
            cached_data = cache_manager.get(int(config_id))
        else:
            return
        
    chain = cached_data["chain"]
    vector_store = cached_data['vector_store']
    request.app.chain = chain
    request.app.vector_store = vector_store
    user_role = query.role

    if user_role == "user":
        user_role = "developer"

    start_time = time.time()

    out = await chain.invoke({
        "question": query.content,
        "context_id": context_id,
        "user_role" : user_role
    })

    chat_context = out.get("chat_context", {})
    out.pop("chat_context", None)
    chat_id = str(uuid.uuid4())
    background_tasks.add_task(save_data, chat_id, context_id, query.content, out, chat_context, user_id,config_id, env_id, db)

    logger.info(f"out:{out}")

    end_time = time.time()
    total_response_time = end_time - start_time
    logger.debug(f"total_response_time:{total_response_time}")
    return {
        "response": out,
        "query": query.content,
        "chat_id": chat_id,
    }


#! This api is not in use right now, instead we are using a scheduler for the feedback_correction job
@MainRouter.post("/feedback_correction", status_code=status.HTTP_201_CREATED)
def feedback_correction(request: Request, body: FeedbackCorrectionRequest):

    """
    Processes feedback from LLM responses and updates the vector store accordingly.

    Args:
        request (Request): FastAPI request object containing the app's vector store.
        body (FeedbackCorrectionRequest): Request body containing user feedback to be processed.

    Returns:
        str: Success message indicating the feedback processing outcome.

    """

    store = request.app.vector_store

    if body.responses:
        for response in body.responses:
            similar_sample = store.find_similar_samples(response.description)
            if len(similar_sample) > 0 and similar_sample[0]['distances'] < 0.3:
                store.update_store(similar_sample[0]['id'],response.metadata,response.description)
            else:
                store.update_store(metadatas = response.metadata,documents = response.description)
        return "Success: Feedback received and processed."

    else:
        return "Success: No Feedback received and processed."



from groq import Groq
from pathlib import Path
import tempfile, time, uuid, os

client = Groq()

TTS_MODEL = "playai-tts"
TTS_VOICE = "Aaliyah-PlayAI"
STT_MODEL = "whisper-large-v3-turbo"


@MainRouter.post("/speech-query", status_code=status.HTTP_201_CREATED)
async def speech_query(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    context_id: str = Query(..., alias="contextId"),
    config_id: str = Query(..., alias="configId"),
    env_id: str = Query(..., alias="envId"),
    user_id: int = Query(..., alias="userId"),
    db: Session = Depends(get_db),
):
    """
    Accepts a speech file, transcribes it, gets LLM answer, returns TTS audio response.
    """

    # --- Step 1: Speech-to-Text (STT)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(await file.read())
        temp_audio_path = Path(temp_audio.name)

    try:
        transcript = client.audio.transcriptions.create(
            model=STT_MODEL,
            file=open(temp_audio_path, "rb"),
            response_format="text"
        )
    except Exception as e:
        os.remove(temp_audio_path)
        raise HTTPException(status_code=500, detail=f"STT Error: {str(e)}")

    os.remove(temp_audio_path)
    transcribed_text = transcript.strip()
    logger.info(f"Transcribed query: {transcribed_text}")

    # --- Step 2: Load Chain & Vector Store
    cached_data = cache_manager.get(int(config_id))
    if not cached_data:
        logger.info("configuration not found in cache. Rebuilding...")
        response = connector.create_yaml(request, int(config_id), db, False)
        if response['success']:
            cached_data = cache_manager.get(int(config_id))
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch config")

    chain = cached_data["chain"]
    vector_store = cached_data['vector_store']
    request.app.chain = chain
    request.app.vector_store = vector_store

    # --- Step 3: Run the chain
    start_time = time.time()
    result = await chain.invoke({
        "question": transcribed_text,
        "context_id": context_id,
        "user_role": "developer"  # force to developer role as in original code
    })
    chat_context = result.get("chat_context", {})
    result.pop("chat_context", None)
    end_time = time.time()

    logger.debug(f"Total response time: {end_time - start_time:.2f}s")
    logger.info(f"LLM response: {result}")

    # --- Step 4: Save background data
    background_tasks.add_task(
        save_data, context_id, transcribed_text, result, chat_context, user_id, config_id, env_id, db
    )

    # --- Step 5: Text-to-Speech (TTS)
    tts_response_text = result.get("answer", "I'm sorry, I couldn't understand that.")
    audio_output_path = Path(tempfile.gettempdir()) / f"{uuid.uuid4()}.wav"
    try:
        with open(audio_output_path, "wb") as out_file:
            tts_response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=TTS_VOICE,
                input=tts_response_text,
                response_format="wav"
            )
            out_file.write(tts_response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")

    return FileResponse(audio_output_path, media_type="audio/wav", filename="response.wav")

