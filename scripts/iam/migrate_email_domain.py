import logging
import os

import oci.exceptions
from oci.identity.identity_client import IdentityClient
from oci.identity_domains import IdentityDomainsClient
from oci import Response as OCIResponse
from oci.identity_domains.models import User

from scripts.iam.delete_domain import get_domain_info
from utils.models import OAuthToken
from utils.tokens import generate_access_token
from utils.utils import create_bulk_request
from config.config import CLIENT_ID, CLIENT_SECRET, TENANCY_OCID

# Enable logging
# logging.getLogger('oci').setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oci')


def migrate_email_domain(client: IdentityClient):
    bulk_operations = []

    # Selecting the domain we are working on
    logger.info("Starting email domain migration, choose a domain to work on:")
    domain_response = get_domain_info(tenancy_id=TENANCY_OCID, client=client)
    domain_url = domain_response.url

    # Create a domains client using domain url from previous response
    identity_domains: IdentityDomainsClient = IdentityDomainsClient(config, domain_url)

    old_email_domain = input("Please provide the old email domain to match users: ")
    new_email_domain = input("Please provide the new email domain: ")

    logger.info("Starting users email domain migration...")

    # TODO add validation so that if no matching emails throw and error and stop code execution.
    # Get list of users with a matching domain old email string
    list_users_response: OCIResponse = identity_domains.list_users(
        filter=f'userName co "{old_email_domain}"',
        attributes='userName, emails'
    )

    # Getting the users list from previous response and give a User type
    users_response: list[User] = list_users_response.data.resources

    logger.info("Creating bulk request...")

    # Modify the patch request for each user and append to bulk operations
    for user in users_response:
        op = {
            "method": "PATCH",
            "path": f"/Users/{user.id}",
            "data": {
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
                "Operations": [
                    {
                        "op": "replace",
                        "path": "userName",
                        "value": user.user_name.replace(f'{old_email_domain}', f'{new_email_domain}')
                    },
                    {
                        "op": "replace",
                        "path": "emails[type eq \"work\"]",
                        "value": [
                            {
                                "value": user.user_name.replace(f'{old_email_domain}', f'{new_email_domain}')
                            }
                        ]
                    },
                    {
                        "op": "replace",
                        "path": "emails[type eq \"recovery\"]",
                        "value": [
                            {
                                "value": user.user_name.replace(f'{old_email_domain}', f'{new_email_domain}')
                            }
                        ]
                    }
                ]
            }
        }

        bulk_operations.append(op)

    # Bulk requests created
    bulk_request = {
        "schemas": [
            "urn:ietf:params:scim:api:messages:2.0:BulkRequest"
        ],
        "Operations": bulk_operations
    }

    # Obtain an access token to send a bulk request to /admin/v1/Bulk
    access_token: OAuthToken = generate_access_token(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        domain_url=domain_url
    )

    try:
        create_bulk_request(
            idcs_host=domain_url,
            token=access_token.access_token,
            data=bulk_request
        )
    except Exception as e:
        logger.error("Unknown error")
        logger.error(e)

    logger.info("Email domain migration succeeded")


if __name__ == "__main__":
    profile_name = (
            input("Please provide your config file profile name (if none selected will be DEFAULT): ") or "DEFAULT"
    ).upper()
    config = oci.config.from_file(profile_name=profile_name)
    identity_client = IdentityClient(config)
    migrate_email_domain(client=identity_client)

