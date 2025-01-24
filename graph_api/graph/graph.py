from langgraph.graph import START, END, StateGraph
from langchain_openai import ChatOpenAI
from db_client import DBClient
from node import State, Node
from doc_vector_store_generator import DocumentVectorStoreGenerator

class Graph:

    def __init__(self, document_path, db_client):

        print("Initializing graph....")

        self.graph_builder = StateGraph(State)
        self.openai_llm = ChatOpenAI(model="gpt-4o-mini")
        self.db_client = db_client

        print("Creating vector store...")
        dvsg = DocumentVectorStoreGenerator()
        dvsg.load_documents(document_path)
        dvsg.create_vector_store()
        print("Vector store created")

        self.vector_store = dvsg.vector_store


    def _build_nodes(self):

        self.graph_builder.add_node(
            "initial_message",
            Node(
                name="initial_message",
                node_type="rag",
                llm=self.openai_llm,
                vector_store=self.vector_store,
                rag_search_argument="message"
            ).callback
        )

        self.graph_builder.add_node(
            "data_query_classification",
            Node(
                name="data_query_classification",
                node_type="llm",
                llm=self.openai_llm,
                save_original_message_as="original_question"
            ).callback
        )

        self.graph_builder.add_node(
            "data_query_processing",
            Node(
                name="data_query_processing",
                node_type="rag",
                llm=self.openai_llm,
                vector_store=self.vector_store,
                rag_search_argument="original_question"
            ).callback
        )

        self.graph_builder.add_node(
            "non_data_query_processing",
            Node(
                name="non_data_query_processing",
                node_type="fixed_response",
                fixed_response="I'm not sure if that's a data request. Right now, I'm only allowed to answer data requests"
            ).callback
        )

        self.graph_builder.add_node(
            "data_query_execution",
            Node(
                name="data_query_execution",
                node_type="data_query",
                db_client=self.db_client
            ).callback
        )

        self.graph_builder.add_node(
            "data_query_execution_failure",
            Node(
                name="data_query_execution_failure",
                node_type="fixed_response",
                fixed_response="""
                I can see that's a data request, but I'm having trouble using the data to answer it.
                Please try again, or try asking the question in a different way.
                """
            ).callback
        )

        self.graph_builder.add_node(
            "data_query_execution_success",
            Node(
                name="data_query_execution_success",
                node_type="llm",
                llm=self.openai_llm,
            ).callback
        )

    def build_graph(self):

        print("Building graph...")

        self._build_nodes()

        self.graph_builder.add_conditional_edges(
            START,
            lambda state: "Initial Message" if state["is_initial_message"] else "Not Initial Message",
            {
                "Initial Message": "initial_message",
                "Not Initial Message": "data_query_classification"
            }
        )

        self.graph_builder.add_conditional_edges(
            "data_query_classification",
            lambda state: "Data Query" if state["message"] == "Data Query" else "Not Data Query",
            {
                "Data Query": "data_query_processing",
                "Not Data Query": "non_data_query_processing"
            }
        )

        self.graph_builder.add_edge("non_data_query_processing", END)

        self.graph_builder.add_edge("data_query_processing", "data_query_execution")

        self.graph_builder.add_conditional_edges(
            "data_query_execution",
            lambda state: "Success" if state["query_successful"] else "Failure",
            {
                "Success": "data_query_execution_success",
                "Failure": "data_query_execution_failure"
            }
        )

        self.graph_builder.add_edge("data_query_execution_success", END)
        self.graph_builder.add_edge("data_query_execution_failure", END)

        print("Graph built")

    def compile(self):

        print("Compiling graph")

        self.graph = self.graph_builder.compile()

        print("Graph compiled")

    def invoke(self, message):

        print(f"Running invocation on message: {message}")

        response = self.graph.invoke({"message": message, "is_initial_message": False})["message"]

        print(f"Response: {response}")

        return response

    def get_initial_message(self):

        response = self.graph.invoke({"message": "Database summary", "is_initial_message": True})["message"]
        print(f"Response: {response}")

        return response


