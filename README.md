# OCI Scripts

## OCI Resources Covered

- 🔒 IAM

## Set Your Environment

For simplicity, it is recommended to install and configure the [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm)
as it will create the config file used by the SDK, from there you gan get the `USER_OCID`, `TENANCY_OCID`, `KEY_FILE_PATH`
and the `OCI_REGION` to copy the `sample.env` file to create your `.env` with your OCI variables.

```
USER_OCID=ocid1.user.oc1..
TENANCY_OCID=ocid1.tenancy.oc1..
KEY_FILE_PATH=/path-to-your-private-key.pem
OCI_REGION=us-phoenix-1
CLIENT_ID=
CLIENT_SECRET=
```

The `config.py` file will use the variables to create CONSTANTS that can be imported and are used over the scripts.

✨ You are good to run the scripts ✨


