from .formatter import Formatter
from loguru import logger
import requests
import json
from app.base.base_plugin import BasePlugin
from app.base.remote_data_plugin import RemoteDataPlugin
from app.base.plugin_metadata_mixin import PluginMetadataMixin
from typing import  Tuple, Optional
from app.readers.base_reader import BaseReader


class Website(BasePlugin, PluginMetadataMixin,RemoteDataPlugin,  Formatter):
    """
    Website class for interacting with website data.
    """

    def __init__(self, connector_name : str, website_url:str, depth : int = 1, headers: str = "{}"):
        super().__init__(__name__)

        self.connection = {}

        self.connector_name = connector_name.replace(' ','_')
        self.params = {
            'url': website_url,
            "depth":  depth,
            "headers": headers,
        }


    def connect(self):
        """
        Mocked connection method for Website.

        :return: Tuple containing connection status (True/False) and an error message if any.
        """
        return True, None


    def healthcheck(self)-> Tuple[bool, Optional[str]]:
        """
        Perform a health check by checking if the Website  is accessible.

        :return: Tuple containing the health status (True/False) and error message (if any).
        """
        logger.info("health check for website")

        url = self.params["url"]

        headers = {}
        try:
            headers = json.loads(self.params.get("headers", "{}"))
        except Exception as e:
            return False, str("Provide valid json for headers")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                logger.info("Website health check passed.")
                return True, None
            else:
                logger.error(f"Health check failed: {response.status_code} {response.text}")
                return False, "Failed to connect with website"
        except Exception as e:
            logger.exception(f"Exception during health check: {str(e)}")
            return False, str(e)


    def fetch_data(self, params=None):

        headers = {}
        try:
            headers = json.loads(self.params.get("headers", "{}"))
        except Exception as e:
            logger.exception(e)

        base_reader = BaseReader({
                                "type": "url",
                                "path": [self.params.get('url')],
                                "depth": int(self.params.get("depth", 1)),
                                "headers": headers,
                            })
        data = base_reader.load_data()
        return data