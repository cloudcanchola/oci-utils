import logging

import oci.exceptions
from oci.identity.identity_client import IdentityClient
from oci.identity.models import Domain
from oci.identity_domains import IdentityDomainsClient
from oci.identity_domains.models import AppStatusChanger

from utils.tokens import generate_access_token

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


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


def deactivate_app(client: IdentityDomainsClient, **kwargs):
    is_opc_service = kwargs.get("is_opc_service")
    app_name = kwargs.get("app_name")
    app_secret = kwargs.get("app_secret")
    app_id = kwargs.get("app_id")
    url = kwargs.get("domain_url")

    # REQUIRED, create a model to indicate what is the desired status
    app_changer_model = AppStatusChanger(
        active=False,
        schemas=["urn:ietf:params:scim:schemas:oracle:idcs:AppStatusChanger"]
    )

    # If opc service an especial token is needed to deactivate the application
    if is_opc_service:
        auth_token = generate_access_token(client_id=app_name, client_secret=app_secret, domain_url=url)
        client.put_app_status_changer(
            app_status_changer_id=app_id,
            authorization=auth_token.access_token,
            app_status_changer=app_changer_model
        )
        logger.info(f"{app_name} application deactivated")
    else:
        # Non opc apps can be deactivated with basic permissions no special token needed
        client.put_app_status_changer(app_status_changer_id=app_id, app_status_changer=app_changer_model)
        logger.info(f"{app_name} Application deactivated")


def deactivate_domain_apps(url: str, client: IdentityDomainsClient):
    """Get all apps from domain to deactivate them"""
    apps = client.list_apps()

    for app in apps.data.resources:
        app_id = app.id
        app_name = app.name
        is_opc_service = app.is_opc_service
        app_secret = app.client_secret

        try:
            deactivate_app(
                client=client,
                is_opc_service=is_opc_service,
                app_id=app_id,
                app_name=app_name,
                app_secret=app_secret,
                domain_url=url
            )
        except oci.exceptions.ServiceError as e:
            logger.info(f"Error deactivating app: {e}")


def delete_identity_domain(
        domain_url: str,
        domain_ocid: str,
        client: IdentityDomainsClient,
        iam_client: IdentityClient
):
    # Domains with active applications won't be deleted
    deactivate_domain_apps(url=domain_url, client=client)
    logger.info("All applications were deactivated, proceeding to delete Domain.")
    try:

        iam_client.deactivate_domain(domain_id=domain_ocid)
        oci.wait_until(
            client=iam_client,
            response=iam_client.get_domain(domain_id=domain_ocid),
            property="lifecycle_state",
            state="INACTIVE",
            max_wait_seconds=120,
            max_interval_seconds=5
        )
        logger.info("Identity Domain successfully deactivated.")
        iam_client.delete_domain(domain_id=domain_ocid)
        logger.info(f"Identity Domain successfully deleted")
        # iam_client.delete_domain(domain_id=domain_ocid)
        # logger.info("Domain deleted successfully.")
    except oci.exceptions.MaximumWaitTimeExceeded as e:
        logger.error("Waiting for domain deactivation timed out.")
    except oci.exceptions.ServiceError as e:
        logger.error(f"Error deleting domain: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    config = oci.config.from_file()
    identity_client = IdentityClient(config)
    d_name, d_ocid, d_url = get_domain_info(tenancy_id=config["tenancy"], client=identity_client)
    identity_domains_client = IdentityDomainsClient(config, d_url)
    delete_identity_domain(
        domain_url=d_url,
        domain_ocid=d_ocid,
        client=identity_domains_client,
        iam_client=identity_client
    )