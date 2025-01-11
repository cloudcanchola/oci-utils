import os
from dotenv import load_dotenv
import yaml

load_dotenv()


def get_env_variable(key, default=None):
    """Retrieve an environment variable or return a default value."""
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value


# Access sensitive variables
USER_OCID = get_env_variable("USER_OCID")
TENANCY_OCID = get_env_variable("TENANCY_OCID")
KEY_FILE_PATH = get_env_variable("KEY_FILE_PATH")
OCI_REGION = get_env_variable("OCI_REGION")
CLIENT_ID = get_env_variable("CLIENT_ID")
CLIENT_SECRET = get_env_variable("CLIENT_SECRET")

