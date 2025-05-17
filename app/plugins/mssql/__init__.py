from app.models.prompt import Prompt
from collections import OrderedDict
from app.models.request import ConnectionArgument

# Plugin Metadata
__version__ = '1.0.0'
__plugin_name__ = 'mssql'
__display_name__ = "MSSQL DB"
__description__ = 'MSSQL integration for handling MSSQL database operations.'
__icon__ = '/assets/plugins/logos/mssql.svg'
__category__ = 2


# Connection arguments
__connection_args__ = OrderedDict(
    db_name= ConnectionArgument(
        type = 1,
        generic_name= 'MSSQL Database name',
        description = 'Database name',
        order= 5,
        required = True,
        value = None,
        slug = "db_name"
    ),
    db_user=ConnectionArgument(
        type= 1,
        generic_name= 'MSSQL User name',
        description= 'Database username',
        order= 2,
        required = True,
        value = None,
        slug = "db_user"
    ),
    db_password=ConnectionArgument(
        type= 2,
        generic_name= 'MSSQL Password',
        description= 'Database password',
        order= 3,
        required = True,
        value = None,
        slug = "db_password"
    ),
    db_server=ConnectionArgument(
        type= 1,
        generic_name= 'MSSQL Database Server',
        description= 'Include port number with a comma in server eg: ip.aaaaaaa.com,9600',
        order= 1,
        required = True,
        value = None,
        slug = "db_server"
    ),
    db_port=ConnectionArgument(
        type= 3,
        generic_name= 'MSSQL Database port',
        description= 'Database port',
        order = 4,
        required = True,
        value = None,
        slug = "db_port"
    ),
)

# Prompt
__prompt__ = Prompt(**{
        "base_prompt": "{system_prompt}{user_prompt}",
        "system_prompt": {
            "template": """
            You are an Mssql expert. Your job is to answer questions about a Mssql database using only the provided schema details and rules.

            Conversation history is provided below:
            -- start chat_history section --
            {recal_history}
            -- end chat_history section --

            go through the schema details given below:
            -- start db schema section--
            {schema}
            -- end db schema section--

            A brief description about the schema is given below:
            -- start db context section--
            {context}
            -- end db context section--

            Strictly consider Sample sql queries with their questions are given below:
            -- start query samples section--
            $suggestions
            -- end query samples section--

            Adhere to the given rules without failure

            -- start rules section --
            - use LIKE operator with LOWER function for string comparison or equality
            - Do not use non existing tables or fields
            - Do not use unwanted joins
            - Do not return incomplete queries
            - Adher to sysql query syntax

            - To retrieve employees with salaries above a specified threshold Use UNION ALL on emp.FinalPayrollforNONTeaching, emp.FinalPayrollforTeaching, and emp.FinalPayrollforStipend, join with mst.PayCycle and mst.FinancialYear for default filters, and apply TRY_CAST(FPN.CurrentBasicSalary AS float) > [threshold]
            -- end rules section --
            """
        },
        "user_prompt":{
            "template": """
            Follow these steps to generate query to solve the question `$question`

            1. Deliberately go through schema, samples, context, rules deliberately
            2. Understand the question and check whether it's doable with the given context
            3. Do only the task asked, Don't hallucinate and overdo the task
            5. Strictly return at least 1 text fields and an id field during aggregation/group by operations
            7. output in the given json format, extra explanation is strictly prohibited
            8. Striclty always consider sample sql queries as a reference to construct the query

            {
                "explanation": "Explain how you finalized the sql query using the schemas,views, samples and rules provided.",
                "query" : "mssql query", //striclty consider sample sql queries as a reference to construct the query
                "operation_kind" : "aggregation|list",
                "schema": "used schema details separated by comma",
                "confidence" : "confidence in 100",
                "visualisation": {
                    "type": "chart type (bar chart, line chart, pie chart) or 'table' for tabular format; 'none' if operation_kind is 'list'",
                    "x-axis": ["fields that can be used as x axis"],
                    "y-axis": ["fields that can be used as y axis"],
                    "title": "layout title name"
                },
                "general_message": "a general message describing the answers like 'here is your list of incidents' or 'look what i found'",
                "empty_message" : "a general message describing if there is no data for the question or random question and request gently to reframe a new question",
                "main_entity" : "main entity  for the query",
            }
            """
        },
        "regeneration_prompt": {
            "template": """
            You were trying to answer the following user question by writing SQL query to answer the question given in `[question][/question]`
            [question]
            $question
            [/question]

            You generated this query given in `[query][/query]`
            [query]
            $query_generated
            [/query]

            But upon execution you encountered some error , error traceback is given in [query_error][/query_error]
            [query_error]
            $exception_log
            [/query_error]

            Follow these steps to generate the query

            1. Deliberately go through schema, samples, context, rules deliberately
            2. Understand the question and check whether it's doable with the given context
            3. Do only the task asked, Don't hallucinate and overdo the task
            4. Strictly return at least 1 text fields and an id field during aggregation/group by operations
            5. output in the given json format, extra explanation is strictly prohibited
            6. Striclty always consider sample sql queries as a reference to construct the query


            {
                "explanation": "Explain how you finalized the sql query using the schemas,views, samples and rules provided. if user quesion matching sample query then generate the query using the sample query",
                "query" : "mssql query", //striclty consider sample sql queries as a reference to construct the query
                "operation_kind" : "aggregation|list",
                "visualisation": {
                    "type": "chart type (bar chart, line chart, pie chart) or 'table' for tabular format; 'none' if operation_kind is 'list'",
                    "value_field": "fields in which values are stored",
                    "x-axis": "field that can be used as x axis",
                    "y-axis": "field that can be used as y axis",
                    "title": "layout title name"
                },
                "schema": "used schema details separated by comma",
                "confidence" : "confidence in 100",
                "general_message": "a general message describing the answers like 'here is your list of incidents' or 'look what i found'",
                "empty_message" : "a general message describing if there is no data for the question or random question and request gently to reframe a new question",
                "main_entity" : "main entity  for the query",
            }
            """
        }
    })



__all__ = [
    __version__, __plugin_name__, __display_name__ , __description__, __icon__, __category__, __prompt__
]