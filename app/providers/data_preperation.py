from loguru import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SourceDocuments:
    def __init__(self,schema_details, schema_configs, documentation):
        self.documentation = []
        self.schema_details = []
        self.schema_configs = schema_configs

        self.documentation.extend(documentation)

        for schema_config in schema_configs:
            table_user_roles = schema_config.get('user_roles', [])
            table_name = schema_config['table_name']
            self.schema_details.append({'content': schema_config.get('ddl',''), 'metadata': {"table_user_roles" : table_user_roles, "table_name" : table_name}})
            table_doc = ''
            table_doc = f"Table Name: {table_name} - {schema_config['description']}\n column are given below\n"
            for column in schema_config['columns']:
                table_doc = f"{table_doc} {column.get('column_name','')} - {column['description']}\n"
            self.documentation.append({'content': table_doc, 'metadata': {"table_user_roles" : table_user_roles, "table_name" : table_name}})


    def get_source_documents(self):
        chunked_docs = []
        chunked_schema = []

        try:

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=20)
            text_splitter_doc = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20,separators=["##"])


            for docs in self.documentation:
                temp_docs = text_splitter_doc.create_documents([str(docs["content"])])
                chunks = text_splitter_doc.split_documents(temp_docs)
                for chunk in chunks:
                    chunk.metadata = docs["metadata"] if "metadata" in docs else {}
                chunked_docs.extend(chunks)
            
            for schema in self.schema_details:
                load_schema = text_splitter.create_documents([str(schema["content"])])
                chunks = text_splitter.split_documents(load_schema)
                for chunk in chunks:
                    chunk.metadata = schema["metadata"] if "metadata" in docs else {}
                chunked_schema.extend(chunks)

        except Exception as e:
            logger.critical(e)

        return chunked_docs, chunked_schema
