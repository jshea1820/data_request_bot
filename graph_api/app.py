from fastapi import FastAPI

from graph_api.utilities.aws_client import AWSClient
from graph_api.langgraph.graph import Graph

app = FastAPI()

LOADED_GRAPHS = {}

@app.get("/")
def read_root():
    return {"message": "Hello from fast API!"}


@app.post("/load_graph")
def read_root(database_name: str = ""):
    
    aws_client = AWSClient()
    aws_client.load_database_info(database_name)

    print("Initializing graph...")
    # Set up the graph
    graph = Graph(
        schema_document_path=f"./graph_api/graph_documents/{database_name}/schema_doc.json",
        db_doc_dir=f"./graph_api/graph_documents/{database_name}/db_docs",
        db_client=aws_client
    )

    print("Building graph...")

    graph.build_graph()
    graph.compile()

    print("Saving graph...")

    LOADED_GRAPHS[database_name] = graph

    print("Success all around")

    return {"message": f"Graph for dataset {database_name} successfully compiled"}

@app.post("/graph_response")
def read_root(database_name: str = "", message: str = ""):

    if database_name not in LOADED_GRAPHS:
        return {"message": f"Graph for database {database_name} is not loaded"}
    
    graph_response = LOADED_GRAPHS[database_name].invoke(message)

    print(f"Graph response: {graph_response}")

    return {"message": graph_response}


@app.get("/list_graphs")
def read_root():

    return {"message": list(LOADED_GRAPHS.keys())}

@app.post("/initial_message")
def read_root(database_name: str = ""):

    if database_name not in LOADED_GRAPHS:
        return {"message": f"Graph for database {database_name} is not loaded"}

    graph_response = LOADED_GRAPHS[database_name].get_initial_message()

    return {"message": graph_response}
    