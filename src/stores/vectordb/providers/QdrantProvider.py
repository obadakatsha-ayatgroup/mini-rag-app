from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from typing import List
import logging
from ..VectorDBEnums import DistanceMethodEnums

class QdrantProvider(VectorDBInterface):
    
    def __init__(self, db_path: str, distance_method: str):
        
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        
        if distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collection(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str,
                          embedding_size: int,
                          do_reset: bool=False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.create_collection(collection_name=collection_name, vectors_config=models.VectorParams(
                size=embedding_size,
                distance=self.distance_method
            ))
            return True
        return False

    def insert_one(self, collection_name: str, txt: str, vector: list,
                    meta_data: dict=None,
                    record_id: str=None):
        
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"can not insert new record to not existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                        models.Record(
                            id=[record_id],
                            vector=vector,
                                    payload={
                                            "text": txt,
                                            "meta_data": meta_data
                                            }
                                    )
                        ]
                    )
        except Exception as e:
            self.logger.error(f"error while inserting one {e}")
            return False
        
        return True
    
    def insert_many(self, collection_name: list, txts: list, vectors: list,
                    meta_data: list=None,
                    record_ids: list=None,
                    batch_size: int=50):
        
        if meta_data is None:
            meta_data = [None] * len(txts)
        
        if record_ids is None:
            record_ids = list(range[0, len(txts)])

        for i in range(0, len(txts), batch_size):
            batch_end = i+batch_size

            batch_txt = txts[i: batch_end]
            batch_vectors = vectors[i: batch_end]
            batch_mata_data = meta_data[i: batch_end]
            batch_records_ids = record_ids[i: batch_end]
            
            batch_records = [
                models.Record(
                id=batch_records_ids[x],
                vector=batch_vectors[x],
                        payload={
                            "text": batch_txt[x],
                            "meta_data": batch_mata_data[x]
                            }
                        )

                for x in range(len(batch_txt))
            ]

            try:
                _ = self.client.upload_records(
                collection_name=collection_name,
                records=batch_records
                )

            except Exception as e:
                self.logger.error(f"error while inserting batch {e}")
                return False

            return True
    
    def search_by_vector(self, collection_name:str, vector: list, limit: int):
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )