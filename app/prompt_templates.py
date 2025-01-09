from langchain_core.prompts import PromptTemplate

prompt_template_strings = {
    "data_query_classification": """

    Classify the following message as either "Data Query" or "Not Data Query". 
    A data query typically asks for specific numerical or factual information, while a non-data query asks for opinions, general knowledge, or abstract concepts. 
    Return just "Data Query" if it is a data query, and "Not Data Query" if it is not a data query.

    Examples:

    1. Message: "What is the capital of France?"
       Output: non-data query
    2. Message: "How many people live in Tokyo?"
       Output: data query
    3. Message: "What is the temperature in Chicago today?"
       Output: data query
    4. Message: "Can you tell me the benefits of eating vegetables?"
       Output: non-data query

    Now classify this message:
    Message: {message}

    """,

    "data_query_processing": """

    The following is documentation for the structure of a relational database:

    "{context}"

    Construct a SQL query on the relational database from the previous documentation to create a
    Postgres SQL query to answer the following question. Return only the valid SQL code and nothing else:

    "{original_question}"

    """,
    "data_query_execution_success": """

    A user asked the following question:

    "{original_question}"

    From that question, a SQL code generator wrote the following query to answer the question:

    "{database_query}"

    After running the query on the database, the results were the following:

    "{query_results}"

    Using the results from the query, answer the user's question.

    """
    
}

PROMPT_TEMPLATES = {}
for node, pts in prompt_template_strings.items():

    PROMPT_TEMPLATES[node] = PromptTemplate.from_template(pts)
