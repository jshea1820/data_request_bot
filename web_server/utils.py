
def extract_query_params(session):

    # Extract database details from query parameters
    query_string = session.input[".clientdata_url_search"]()[1:]

    query_param_strings = query_string.split("&")
    query_params = {
        query_param_string.split("=")[0]: query_param_string.split("=")[1] for query_param_string in query_param_strings
    }
    
    return query_params

