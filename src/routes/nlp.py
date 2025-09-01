from fastapi import FastAPI, APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController, NLPController
import aiofiles  # type: ignore
from models import ResponseSignal
import logging
from .schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk, Asset
from models.AssetModel import AssetModel
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import NLPController
import os


logger = logging.getLogger('uvicorn.error')
nlp_router = APIRouter(
    prefix='/api/v1/nlp',
    tags=['api_v1', 'nlp'],
)

@nlp_router.post('index/push/{project_id}')
async def index_project(request: Request, project_id: str, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                generation_client=request.app.generation_client,
                                embedding_client=request.app.embedding_client)
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx=0
    
    while has_records:
        chunks = await chunk_model.get_projects_chunks(project_id=project.id, page_no=page_no)

        if len(chunks):
            page_no+=1
        if not chunks or len(chunks)==0:
            has_records=False
            break
        
        chunks_ids = list(range(idx, idx + len(chunks)))
        idx += len(chunks)

        is_inserted = nlp_controller.index_into_vectordb(project=project, chunks=chunks, do_reset=push_request.do_reset, chunks_ids=chunks_ids)

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_DB_ERROR.value
                }
            )
        
        inserted_items_count += len(chunks)
        
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get('index/info/{project_id}')
async def get_project_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                generation_client=request.app.generation_client,
                                embedding_client=request.app.embedding_client)
    
    collection_info = nlp_controller.get_vectordb_collection_info(project=project)

    return JSONResponse(
            content={
                "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
                "collection info": collection_info
            }
        )


@nlp_router.post('index/search/{project_id}')
async def search_index(request: Request, project_id: str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)


    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                generation_client=request.app.generation_client,
                                embedding_client=request.app.embedding_client)
    
    results = nlp_controller.search_vectordb_collection(project=project, text=search_request.text, limit=search_request.limit)

    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": results
        }
    )