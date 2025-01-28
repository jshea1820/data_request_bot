from fastapi import FastAPI
import boto3
import json
import os
import pandas as pd

from graph_api.utilities.utils import unpack_param_store, AWS_SESSION
from graph_api.utilities.aws_db_client import AWSDBClient
from graph_api.langgraph.graph import Graph

app = FastAPI()

LOADED_GRAPHS = {}

@app.get("/")
def read_root():
    return {"message": "Hello from fast API!"}


@app.post("/load_graph")
def read_root(database_name: str = ""):

    # Start by unpacking the needed parameters from parameter store
    print("Unpacking params...")
    ssm_client = AWS_SESSION.client("ssm")
    params = unpack_param_store(database_name, ssm_client)
    print("Params")
    print(params)

    print("Initializig session...")
    # Next initialize the session with glue using unpacked params
    user_account_session = boto3.Session(
        aws_access_key_id=params["aws_access_key"],
        aws_secret_access_key=params["aws_access_secret_key"],
        aws_session_token=params["aws_session_token"],
        region_name=params["aws_region"]
    )

    print("Establishing DB connection...")
    aws_db_client = AWSDBClient(
        database_name=params["glue_database_name"],
        session=user_account_session
    )

    print("Generating schema docs...")
    # Generate the database schema document
    schema_docs = aws_db_client.get_schema_docs()

    print("Saving schema docs to file...")

    # Write the schema doc to local storage
    doc_dir = f"./graph_api/graph_documents/{database_name}"
    doc_path = f"{doc_dir}/schema_doc.json"
    os.makedirs(doc_dir, exist_ok=True)
    with open(doc_path, "w") as json_file:
        json.dump(schema_docs, json_file, indent=4)

    print("Initializing graph...")
    # Set up the graph
    graph = Graph(
        document_path=doc_path,
        db_client=aws_db_client
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
    