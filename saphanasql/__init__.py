import logging
import azure.functions as func
import subprocess
import tempfile
import os

HDBSQL_RELATIVE_PATH = "hdbclient/hdbsql"

DB_USER = os.environ['DB_USER']
DB_USER_SECRET = os.environ['DB_USER_SECRET']
SID = os.environ['SID']
TARGETDB = os.environ['TARGETDB']

def main(req: func.HttpRequest, 
        context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Interact with query parameters or the body of the request.
    SQL = req.params.get("SQL")
    if SQL is None:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            SQL = req_body.get("SQL")

    # Write the SQL command to the temporary file
    tempFilePath = tempfile.gettempdir()
    fp = tempfile.NamedTemporaryFile()
    fp.write(bytes(SQL, 'utf-8'))
    fp.flush()

    logging.info('file written')

    # Execute /usr/sap/hdbclient/hdbsql command and capture the output
    hdbsql_path = "/".join([str(context.function_directory), HDBSQL_RELATIVE_PATH])
    command = [hdbsql_path, "-d", SID, "-n", TARGETDB, "-u", DB_USER, "-p", DB_USER_SECRET, "-I", fp.name]
    try:
        logging.info('about to run hdbsql')
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        logging.info('hdbsql executed')
        body = output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        body = f"Error executing command: {e.output.decode('utf-8')}"

    # Return the response body
    return func.HttpResponse(body, status_code=200)
