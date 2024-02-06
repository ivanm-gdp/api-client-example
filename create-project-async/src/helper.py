from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from os import path
import json
from functools import cmp_to_key


def get_access_token(base_url, client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(
        token_url=base_url + "/api/oauth/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    return token["access_token"]


def get_operations(file_name):
    with open(file_name, "r") as file:
        return json.loads(file.read())


def pair_files(filepaths: list[str]):
    valid_extras_extension = ["txt", "json", "json"]

    def filepath_compare_function(filepath1, filepath2):
        _, filename1 = path.split(filepath1)
        _, filename2 = path.split(filepath2)

        name1, extension1 = filename1.split(".")
        name2, extension2 = filename2.split(".")

        if name1 == name2:
            if extension1 in valid_extras_extension:
                return 1

            if extension2 in valid_extras_extension:
                return -1

        return name1 < name2

    document_with_extras = {}
    sorted_filepaths = sorted(filepaths, key=cmp_to_key(filepath_compare_function))

    for filepath in sorted_filepaths:
        _, filename_with_extension = path.split(filepath)
        filename = filename_with_extension.split(".")[0]

        if filename in document_with_extras:
            document_with_extras[filename]["extras"].append(filepath)
        else:
            document_with_extras[filename] = {"document": filepath, "extras": []}

    return list(document_with_extras.values())


def should_group_documents(filepaths: list[str], operations):
    """
    operations: JSON payload for project creation
    """

    filename_count = {}
    for filepath in filepaths:
        _, filename_with_extension = path.split(filepath)
        filename = filename_with_extension.split(".")[0]
        filename_count[filename] = filename_count.get(filename, 0) + 1

    for _, value in filename_count.items():
        if value > 1 and "TOKEN_BASED" in operations["variables"]["input"]["kinds"]:
            return True

    return False
