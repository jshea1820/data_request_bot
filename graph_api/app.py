from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():

    return {"message": "Hello from fast API!"}


@app.get("/load_dataset")
def read_root(dataset_name: str = ""):

    # Establish connection with Glue

    # Set up the graph

    return {"message": f"Your requested dataset is {dataset_name}"}