import json
import logging

import requests
from oci.identity import IdentityClient
from oci.identity.models import Domain

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


def create_bulk_request(idcs_host: str, token :str, data: object):
    """
    This functions calls the /Bulk endpoint executing all the operations
    in the data object.
    :param idcs_host: The Domain/IDCS url
    :param token: An OAuth token used to query IDCS API
    :param data: The Payload that will be sent to /Bulk endpoint
    :return: Bulk response status code
    """
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


def display_domains_menu(domains_list: list):
    """Creates a options menu with all the Identity iam found"""
    print("Domains found on tenancy:")
    for i, domain in enumerate(domains_list, start=1):
        print(f"{i}) {domain.display_name}")


def get_all_domains_info(compartments_list, client: IdentityClient):
    return [
        domain
        for compartment in compartments_list
        for domain in client.list_domains(compartment_id=compartment).data
    ]


def get_domain_info(tenancy_id, client: IdentityClient) -> Domain:
    """Get the selected domain information to deactivate"""
    try:
        compartments_data = client.list_compartments(compartment_id=tenancy_id, compartment_id_in_subtree=True)
        compartments_list = [compartment.id for compartment in compartments_data.data]
        compartments_list.append(tenancy_id)

        # Getting all iam domains info to be used as a list
        domains_info = get_all_domains_info(compartments_list=compartments_list, client=client)

        # Display menu based on iam info
        display_domains_menu(domains_list=domains_info)

        option = int(input("Select an option from Domain list: "))
        if option in range(1, len(domains_info) + 1):
            selected_domain = domains_info[option - 1]
            return selected_domain
        else:
            logger.info("Invalid selection.")
    except ValueError:
        logger.error("Please enter a valid number.")
