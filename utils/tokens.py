import base64
import json

import requests

from utils.models import OAuthToken


def generate_access_token(
        client_id: str,
        client_secret: str,
        domain_url: str
) -> OAuthToken:
    """
    Helper method to get an OAuth token, it can be used to
    make requests to IDCS APIs.
    """
    token_endpoint = f"{domain_url}/oauth2/v1/token"
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode("ascii")).decode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "urn:opc:idm:__myscopes__"
    }

    response = requests.request(url=token_endpoint, headers=headers, data=data, method="POST")
    auth_token = json.loads(response.content.decode("utf-8"))
    return auth_token

