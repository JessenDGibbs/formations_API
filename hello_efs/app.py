import json
from pathlib import Path
import networkx as nx

# You can reference EFS files by including your local mount path, and then
# treat them like any other file. Local invokes may not work with this, however,
# as the file/folders may not be present in the container.
FILE = Path("/mnt/lambda/file")

def create_plan(input_graph_data):
    G = nx.Graph() #create empty grpah
    G.add_nodes_from([(str(key), input_graph_data[key]) for key in input_graph_data if key != 'adjs']) #add nodes from the rooms dictionary
    G.add_edges_from(input_graph_data['adjs'])

def lambda_handler(event, context):
    wrote_file = False
    contents = None
    # The files in EFS are not only persistent across executions, but if multiple
    # Lambda functions are mounted to the same EFS file system, you can read and
    # write files from either function.
    if not FILE.is_file():
        with open(FILE, 'w') as f:
            contents = "Hello, EFS!\n"
            f.write(contents)
            wrote_file = True
    else:
        with open(FILE, 'r') as f:
            contents = f.read()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "file_contents": contents,
            "created_file": wrote_file,
            "Release": 1.0,
            "userData": event["queryStringParameters"],
            "test": "hi"
        }),
    }
