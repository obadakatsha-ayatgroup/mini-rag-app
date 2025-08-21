from ..LLMInterface import LLMInterface
import cohere
import logging
from ..LLMEnums import CoHereEnum, DocumentType

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_char: int=1000,
                 default_generation_output_max_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_output_max_tokens = default_generation_output_max_tokens
        self.default_generation_temperature = default_generation_temperature
    
        self.generation_model_id: str = None
        self.embedding_model_id: str = None
        self.embedding_size: int = None
    
        self.client = cohere.Client(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_txt(self, txt: str):
        return txt[:self.default_input_max_char].strip()
    
    def generate_txt(self, prompt: str, chat_history: list=None, max_output_token: int=None,
                     temperature: float=None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("generation model for CoHere was not set")
            return None
        
        max_output_token = max_output_token if max_output_token else self.default_generation_output_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_txt(txt=prompt),
            temperature=temperature,
            max_tokens=max_output_token
        )
        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        return response.text
    
    def embed_txt(self, txt: str, document_type: str=None):
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        input_type = CoHereEnum.DOCUMENT.value
        if document_type == DocumentType.QUERY.value:
            input_type = CoHereEnum.QUERY.value
        
        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_txt(txt)],
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float_:
            self.logger.error("Error while Embedding text with CoHere")
            return None
        return response.embeddings.float_[0]
   
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt 
        }