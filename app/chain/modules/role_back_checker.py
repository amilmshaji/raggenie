from app.base.abstract_handlers import AbstractHandler
from typing import Any
from loguru import logger
from app.providers.config import configs
from app.chain.formatter.general_response import Formatter


class RoleBackAccessChecker(AbstractHandler):

    def __init__(self, common_context, datasource, roleback_context) -> None:
        """
        Initialize the Executer.

        Args:
            common_context (Dict[str, Any]): The common context shared across handlers.
            datasource (Dict[str, Any]): A dictionary of datasources keyed by intent.
            fallback_handler (AbstractHandler): The handler to call in case of errors.
        """

        self.roleback_context = roleback_context
        self.common_context = common_context
        self.datasource = datasource

    async def handle(self, request: Any) -> str:
        """
        Handle the incoming request by executing the query.

        Args:
            request (Dict[str, Any]): The incoming request to be processed.

        Returns:
            str: The response after processing the request.
        """
        logger.info("passing through => executor")

        response = request

        inference = request.get("inference", {})
        user_role = request.get("user_role","").lower()
        logger.info(f"user_role:{user_role}")
        main_schema = inference.get("main_schema")
        logger.debug(f"main_schema:{main_schema}")

        valid_user_status = False
        if main_schema == "N/A" or main_schema == "n/a"or main_schema == "" or main_schema == "none" or not main_schema or main_schema == "None":
            valid_user_status = True
        elif main_schema:
            datasource = response["rag_filters"]["datasources"][0]
            documents = self.roleback_context.get(datasource)
            if documents:
                for doc in documents:
                    table_name = doc.get('table_name', '')
                    logger.info(f"table_name:{table_name}")
                    if table_name.strip().lower() == main_schema.strip().lower():
                        valid_user_roles = doc.get("user_roles",[])
                        logger.info(f"valid_user_roles:{valid_user_roles}")
                        if user_role in valid_user_roles:
                            valid_user_status = True
                            break

        if not valid_user_status:
            return Formatter.format("Unfortunately, you don't have the necessary permissions to view this information. Please reach out to your administrator if you need access.","")

        return await super().handle(response)
