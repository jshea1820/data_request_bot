
import requests
import os
import time

class GraphAPIClient():

    def __init__(self):

        self.endpoint = "http://{}:{}".format(
            os.environ["GRAPH_API_ENDPOINT"],
            os.environ["GRAPH_API_PORT"]
        )

    def load_graph(self, database_name):

        full_load_graph_url = "{}/load_graph?database_name={}".format(
            self.endpoint,
            database_name
        )

        try:
            response = requests.post(full_load_graph_url)
            print(f"Graph load for database {database_name} successful")

        except requests.exceptions.ConnectionError:
            print("Connection failed")

    def get_graph_response(self, database_name, message):

        invoke_url = "{}/graph_response".format(
            self.endpoint
        )

        params = {
            "database_name": database_name,
            "message": message
        }

        api_response = requests.post(invoke_url, params=params)
        api_response_status_code = api_response.status_code
        api_response_json = api_response.json()

        if api_response_status_code == 200:
            return api_response_json["message"]
        else:
            return "There was a problem handling your request"


    def get_initial_message(self, database_name):

        initial_message_url = "{}/initial_message?database_name={}".format(
            self.endpoint,
            database_name
        )

        response = requests.post(initial_message_url)
        response_status_code = response.status_code
        response_json = response.json()

        if response_status_code == 200:
            return response_json["message"]
        else:
            return "There was a problem"

