"""
FastAPI Resume Builder Backend - AWS Lambda Version
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import os
import logging
import json

from utils.file_parser import extract_text_from_file
from utils.ai_parser import stream_resume_processing

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Builder API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Resume Builder API is running"}

@app.post("/api/stream-resume-processing")
async def stream_resume_processing_endpoint(file: UploadFile = File(...)):
    """Stream resume processing endpoint - Function URL with 5 minute timeout"""
    try:
        logger.info(f"Processing file: {file.filename} ({file.content_type})")
        
        temp_file_path = f"/tmp/{file.filename}"
        content = await file.read()
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        try:
            # Extract text from file - no timeout worries with Function URLs
            extracted_text = extract_text_from_file(temp_file_path)


            async def generate_stream():
                async for chunk in stream_resume_processing(extracted_text):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                }
            )
        finally:
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.error(f"❌ Error cleaning up temp file: {cleanup_error}")

    except Exception as e:
        logger.error(f"❌ Error in streaming processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
