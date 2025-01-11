import json
import logging

import requests

# Enable logging
logging.getLogger('oci').setLevel(logging.INFO)
logging.basicConfig()
logger = logging.getLogger()


def prompt_input(
        prompt,
        validation_fn=None,
        error_message="Invalid input. Please try again.",
        required=True
):
    """
        Prompt the user for input with optional validation.
        Args:
            prompt (str): The message to show the user.
            validation_fn (function): A function to validate the input (optional).
            error_message (str): The error message to display on invalid input.
            required (bool): Whether the input is required or optional.

        Returns:
            str: The validated user input.
    """
    while True:
        user_input = input(prompt).strip()

        # Handle optional input
        if not user_input and not required:
            return None

        # Validate input if validation function is provided
        if validation_fn is None or validation_fn(user_input):
            return user_input

        print(error_message)


def create_bulk_request(idcs_host, token, data):
    endpoint = f"{idcs_host}/admin/v1/Bulk"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    bulk_response = requests.request(
        method="POST",
        url=endpoint,
        headers=headers,
        data=json.dumps(data)
    )

    return bulk_response
