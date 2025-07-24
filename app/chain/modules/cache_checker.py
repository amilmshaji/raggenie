from typing import Any
from loguru import logger
from app.base.abstract_handlers import AbstractHandler
from app.providers.container import Container
import time
import asyncio
from app.providers.config import configs

class Cachechecker(AbstractHandler):
    """
    A handler class for checking and managing cache operations.

    This class extends AbstractHandler and provides functionality to check
    if a query exists in the cache and handle the response accordingly.
    """

    def __init__(self,common_context, datasources, cachestore, forward_handler = None, forward: bool = False) -> None:
        """
        Initialize the Cachechecker.

        Args:
            common_context: The common context shared across handlers.
            Cachestore: The cache storage mechanism.
            forward_handler: The next handler in the chain.
            forward (bool): Whether to forward the request to the next handler.
        """
        self.cache = cachestore
        self.forward_handler = forward_handler
        self.forward = forward
        self.common_context = common_context
        self.context_relevance_threshold = 4
        self.datasources = datasources




    async def handle(self, request: Any) -> str:
        """
        Handle the incoming request by checking the cache

        Args:
            request (Any): The incoming request to be processed.

        Returns:
            str: The response after processing the request.
        """
        logger.info("passing through => cache_checker")

        response = request
        question = request.get("question", "")

        start_time = time.time()
        if configs.answer_from_enabled:
            datasource = configs.answer_from
            results = [await self.cache.find_similar_cache(datasource, question)]

        else:
            tasks = [
                    self.cache.find_similar_cache(datasource, question)
                    for datasource in self.datasources
                ]
            results = await asyncio.gather(*tasks)

        end_time = time.time()
        time_taken = end_time - start_time
        logger.info(f"Time taken for cache retriever: {time_taken}")

        logger.info("sorting retrieved cache")
        for index, out in enumerate(results):
            opt_cache = []
            if out and len(out) > 0 and out[0]['distances'] < self.context_relevance_threshold:
                distances = [doc['distances'] for doc in out]
                if len(out) > 5:
                    clusters = Container.clustering().kmeans(distances, 2)
                    shortest_cluster = clusters[0]
                    for doc in out:
                        if doc['distances'] in shortest_cluster:
                            opt_cache.append(doc)
                else:
                    opt_cache = out

            if "rag" not in response:
                response["rag"]= {"suggestions" : {}}

            response["rag"]["suggestions"] = {list(self.datasources.keys())[index] : opt_cache}


        if self.forward and len(results) > 0:
            if results[0]["distances"] < -10:
                result = results[0]["metadatas"]
                logger.info("query retrieved from cache")
                return await self.forward_handler.handle({"inference":result})

        logger.info("query not retrieved from cache")
        return await super().handle(response)
