from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles  # type: ignore
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from langchain_core.documents import Document



logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1', 'data'],
)

@data_router.post('/upload/{project_id}')
async def upload_data(project_id: str, file: UploadFile,
                        app_setting:Settings=Depends(get_settings)) -> JSONResponse:

    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":result_signal,
            }    
        )
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = DataController().generate_unique_file_path(origin_file_name=file.filename,
                                                            project_id=project_id)
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_setting.FILE_DEFAULT_CHUNK_SIZE):
              await  f.write(chunk)

    except Exception as e:
        logger.error(f'Error while uploading file {e}')
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal":ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            'file id': file_id
        }
    )
    
@data_router.post('/process/{project_id}')
async def process_endpoint(project_id: str, process_request: ProcessRequest) -> JSONResponse | list[Document]:
    
    file_id = process_request.file_id
    chunk_size = process_request.chunck_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )
    
    if file_chunks is None or len(file_chunks)==0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "signal": ResponseSignal.PROCESSING_FAILED.value
                            })
    
    return file_chunks