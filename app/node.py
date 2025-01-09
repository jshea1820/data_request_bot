from typing_extensions import List, TypedDict
from langchain_core.documents import Document
from prompt_templates import PROMPT_TEMPLATES

class State(TypedDict):
    original_question: str
    message: str
    database_query: str
    query_results: str
    query_successful: bool
    is_initial_message: bool
    context: List[Document]

class Node:

    def __init__(
        self,
        name=None,
        node_type=None,
        llm=None,
        fixed_response=None,
        vector_store=None,
        rag_search_argument=None,
        save_original_message_as=None,
        db_client=None
    ):

        self.name = name
        self.node_type = node_type
        self.llm = llm
        self.fixed_response = fixed_response
        self.vector_store = vector_store
        self.rag_search_argument = rag_search_argument
        self.save_original_message_as = save_original_message_as
        self.db_client = db_client

    def callback(self, state: State):

        print(f"Executing node {self.name}")

        if self.node_type == "llm":
            print("LLM node")

            prompt = PROMPT_TEMPLATES[self.name].format(**state)

            print(f"Prompt to execute: {prompt}")

            response = self.llm.invoke(prompt).content

            print(f"LLM response: {response}")

            if self.save_original_message_as:
                return {"message": response, self.save_original_message_as: state["message"]}
            else:
                return {"message": response}
        
        elif self.node_type == "fixed_response":
            print("Fixed response node")

            return {"message": self.fixed_response}
        
        elif self.node_type == "rag":
            print("Rag node")

            retrieved_docs = self.vector_store.similarity_search(state[self.rag_search_argument])
            docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

            print(f"Retrieved context length: {len(docs_content)}")

            adj_state = state.copy()
            adj_state["context"] = docs_content

            prompt = PROMPT_TEMPLATES[self.name].format(**adj_state)

            response = self.llm.invoke(prompt).content

            print(f"LLM response: {response}")

            return {"message": response, "context": retrieved_docs}
        
        elif self.node_type == "data_query":

            database_query = state["message"][6:-3]

            print(f"Query to exeute: {database_query}")

            try:
                query_results = self.db_client.query(database_query)
                query_results_string = query_results.to_csv(index=False)
                query_success = True
                print("Query success")
                print(f"Query results: {query_results}")
            except Exception as e:
                query_results_string = ""
                query_success = False
                print(f"Query failure: {e}")

            return {
                "message": query_results_string,
                "database_query": database_query,
                "query_results": query_results_string,
                "query_successful": query_success
            }

