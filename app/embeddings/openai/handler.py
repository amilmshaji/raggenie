
import chromadb.utils.embedding_functions as embedding_functions
from loguru import logger


class OpenAIEm:

    def __init__(self,model_name:str = "",api_key:str = ""):
        logger.info("Initialising embedding providers")
        self.ef = embedding_functions.OpenAIEmbeddingFunction(api_key=api_key,  model_name= model_name)

    def load_emb(self):
        return self.ef

    def health_check(self) -> None:
        pass