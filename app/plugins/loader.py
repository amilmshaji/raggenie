from app.plugins.mssql.handler import Mssql
from loguru import logger


class DSLoader:
    def __init__(self, configs):
        self.config = configs

    def load_ds(self):
        db_classes = {
            "mssql": Mssql,
        }
        db_type = self.config.get("type","")
        connection_params = self.config.get("params",{})
        connector_name = self.config.get("connector_name","default")

        logger.info(f"initialising {db_type}")

        db_class = db_classes.get(db_type)
        if db_class:
            try:
                ds = db_class(connector_name=connector_name,**connection_params)
                return ds
            except Exception as e:
                raise e

        else:
            logger.warning("Invalid database type specified in configuration.")
            return None