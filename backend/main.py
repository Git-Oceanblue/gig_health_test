"""
FastAPI Resume Builder Backend - AWS Lambda Version
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import os
import logging
import json
from datetime import datetime

from utils.file_parser import extract_text_from_file
from utils.ai_parser import stream_resume_processing

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Builder API", version="1.0.0")

# Note: CORS is handled by AWS Lambda Function URLs automatically

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
            # Extract text from file - no timeout worries with Function URLs!
            extracted_text = extract_text_from_file(temp_file_path)


            async def generate_stream():
                try:
                    async for chunk in stream_resume_processing(extracted_text):
                        # Ensure proper SSE format with explicit flush
                        event_data = json.dumps(chunk, ensure_ascii=False)
                        yield f"data: {event_data}\n\n"
                        
                    # Send completion signal
                    yield "data: [DONE]\n\n"
                except Exception as stream_error:
                    logger.error(f"❌ Streaming error: {stream_error}")
                    error_data = json.dumps({
                        'type': 'error',
                        'message': f'Streaming error: {str(stream_error)}',
                        'timestamp': datetime.now().isoformat()
                    })
                    yield f"data: {error_data}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # Disable nginx buffering
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


class DbInsertRequest(BaseModel):
    """Request model for database insertion"""
    tableName: str
    data: Dict[str, Any]


class TableMetadataRequest(BaseModel):
    """Request model for table metadata with resume data"""
    resumeData: Dict[str, Any]


@app.post("/api/db/table-metadata")
async def get_table_metadata(request: TableMetadataRequest):
    """
    POST endpoint to retrieve database table metadata
    Accepts resume data and returns columns based on the data keys
    This ensures columns match the actual resume data structure
    """
    try:
        logger.info("Fetching table metadata from resume data...")

        # Extract columns from the provided resume data keys
        if request.resumeData:
            columns = list(request.resumeData.keys())
            logger.info(f"✓ Generated {len(columns)} columns from resume data keys: {columns}")
        else:
            raise ValueError("resumeData cannot be empty")

        table_name = "resumes"

        return {
            "tableName": table_name,
            "columns": columns
        }

    except Exception as e:
        logger.error(f"❌ Error fetching table metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching table metadata: {str(e)}")


@app.post("/api/db/insert-resume")
async def insert_resume_to_db(request: DbInsertRequest):
    """
    POST endpoint to insert resume data into the database
    Expects: { tableName: str, data: { field: value, ... } }
    Returns: { success: bool, message: str }
    """
    try:
        logger.info(f"Received insert request for table '{request.tableName}'")
        logger.info(f"Data keys: {list(request.data.keys())}")

        # Validate input
        if not request.tableName:
            raise ValueError("tableName is required")
        if not request.data:
            raise ValueError("data object cannot be empty")

        # Call the database insertion function
        main_insert(request.data, request.tableName)

        logger.info(f"✓ Data successfully inserted into table '{request.tableName}'")

        return {
            "success": True,
            "message": f"✓ Resume data successfully inserted into '{request.tableName}' table",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error inserting resume data: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Failed to insert data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )
