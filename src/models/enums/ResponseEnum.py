from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "file validated successfully"
    FILE_TYPE_NOT_SUPPORTED = "file type not supported"
    FILE_SIZE_EXCEEDED = "file size exceeded"
    FILE_UPLOAD_SUCCESS = " file uploaded successfully"
    FILE_UPLOAD_FAILED = "file uploaded failed"
    PROCESSING_FAILED = "processing failed"
    PROCESSING_SUCESS = "processing SUCCESS"
    NO_FILES_ERROR = "no found file"
    FILE_ID_ERROR = "no file found with this id"
    PROJECT_NOT_FOUND_ERROR = "project not found error"
    INSERT_INTO_VECTORDB_ERROR = "insert into vector db error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert into vector db success"
    VECTORDB_COLLECTION_RETRIEVED = " vectordb collection retrieved"
    VECTORDB_SEARCH_ERROR = "vectordb seach error"
    VECTORDB_SEARCH_SUCCESS = "vectordb search success"
    RAG_ANSWER_ERROR = "rag answer error"
    RAG_ANSWER_SUCCESS = "rag answer success"
    DATA_PUSH_TASK_READY="data_push_task_ready"
    PROCESS_AND_PUSH_WORKFLOW_READY="process_and_push_workflow_ready"

