from ..LLMInterface import LLMInterface
from openai import OpenAI
import logging
from ..LLMEnums import OpenAIEnum
from typing import Union, List

class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str=None,
                 default_input_max_char: int=1000,
                 default_generation_output_max_tokens: int=1000,
                 default_generation_temperature: float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max_char = default_input_max_char
        self.default_generation_output_max_tokens = default_generation_output_max_tokens
        self.default_generation_temperature = default_generation_temperature
    
        self.generation_model_id: str = None
        self.embedding_model_id: str = None
        self.embedding_size: int = None
    
        self.client = OpenAI(api_key=self.api_key,
                            base_url=self.api_url if self.api_url and len(self.api_url) else None)
        self.enums = OpenAIEnum
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
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error("generation model for OpenAI was not set")
            return None
        
        max_output_token = max_output_token if max_output_token else self.default_generation_output_max_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        chat_history.append(self.construct_prompt(prompt=prompt, role=OpenAIEnum.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature
        )
        if not response or not response.choices or len(response.choices)==0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None
        return response.choices[0].message.content
    
    def embed_txt(self, txt: Union[str, List[str]], document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if isinstance(txt, str):
            txt = [txt]

        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=txt,
        )
        if not response or response.data or len(response.data)==0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None
        
        return [ record.embedding for record in response.data]
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }