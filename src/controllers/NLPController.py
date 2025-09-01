from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentType
from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    def index_into_vectordb(self, project: Project, chunks: List[DataChunk], chunks_ids: list, do_reset:int=0):
        # get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # manage items
        text = [record.chunk_text for record in chunks]
        meta_data = [record.chunk_meta_data for record in chunks]

        vectors = [
            self.embedding_client.embed_txt(txt=txt, document_type=DocumentType.DOCUMENT.value)
            for txt in text
        ]

        # create collection if exist
        _ = self.vectordb_client.create_collection(collection_name=collection_name,
                          embedding_size=self.embedding_client.embedding_size,
                          do_reset=do_reset)
        # insert into vectordb
        _ = self.vectordb_client.insert_many(collection_name=collection_name,
                                            txts=text,
                                            vectors=vectors,
                                            meta_data=meta_data,
                                            record_ids=chunks_ids
                                            )
        
        return True
    
    def search_vectordb_collection(self, project: Project, text: str, limit: int=10):

        # get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # get text embedding vector
        vector = self.embedding_client.embed_txt(txt=text, document_type=DocumentType.QUERY.value)

        if not vector or len(vector)==0:
            return False
        
        # do semantic search
        results = self.vectordb_client.search_by_vector(collection_name=collection_name, vector=vector, limit=limit)

        if not results:
            return False
        
        return json.loads(
            json.dumps(results, default=lambda x: x.__dict__)
        )