from app.models.prompt import Prompt
from collections import OrderedDict
from app.models.request import ConnectionArgument

# Plugin Metadata
__version__ = '1.0.0'
__plugin_name__ = 'website'
__display_name__ = 'Website loader'
__description__ = 'Website integration for handling website data'
__icon__ = '/assets/plugins/logos/website.svg'
__category__ = 1


# Connection arguments
__connection_args__ = OrderedDict(
    website_url= ConnectionArgument(
        type = 4,
        generic_name= 'Website URL',
        description = 'URL of website',
        order = 1,
        required = True,
        value = None,
        slug = "website_url"
    ),
    headers=ConnectionArgument(
        type= 7,
        generic_name= 'Headers to be used',
        description= 'Provide required headers',
        order= 2,
        required = True,
        value = None,
        slug = "headers"
    ),
    depth=ConnectionArgument(
        type= 3,
        generic_name= 'Depth of scanning',
        description= 'Choose the depth of scanning for child URLs. Set to 0 to scan all',
        order= 3,
        required = True,
        value=None,
        slug = "depth"
    )
)

# Prompt
__prompt__ = Prompt(**{
        "base_prompt": "{system_prompt}{user_prompt}",
        "system_prompt": {
            "template": """
            You are an Chatbot designed to answer user questions based only on the context and samples given to you.
            Use the details enclosed in `[context][/context]` to generate answer

            [context]
            {context}
            [/context]

            Strictly consider Sample answers with their questions are given below:
            -- start answer samples section--
            $suggestions
            -- end answer samples section--

            Adhere to these rules while generating answer:
            - Deliberately go through the question and context, samples word by word to appropriately answer the question
            - answer in a human interactive way in polite and friendly manner
            """
        },
        "user_prompt":{
            "template": """
            User question is "$question"
            generate a json in the following format without any formatting.
            {
                "explanation": "Explain how you finalized the answer using the context,samples and rules provided",
                "operation_kind" : "none",
                "general_message": "Answer to user question in human readable Markdown format based on the context and samples",
                "confidence" : "confidence in 100",
                "main_entity": "document"
            }
            """
        },
        "regeneration_prompt": {
            "template": """
            User question is "$question"
            generate a json in the following format without any formatting.
            {
                "explanation": "Explain how you finalized the answer using the context,samples and rules provided",
                "operation_kind" : "none",
                "general_message": "Answer to user question in human readable Markdown format based on the context and samples",
                "confidence" : "confidence in 100",
                "main_entity": "document"
            }
            """
        }
    })



__all__ = [
    __version__, __plugin_name__, __display_name__ , __description__, __icon__, __category__, __prompt__
]