import boto3
import botocore
import itertools
from repository.ssoadmin_repository import SsoAdminRepository
from repository.account_repository import AccountRepository
import logging

PROFILE='fancyprofile'
boto3_session = boto3.session.Session(profile_name=PROFILE)

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    sso_admin_client = boto3_session.client('sso-admin')
    organizations_client = boto3_session.client('organizations')
    identitystore_client = boto3_session.client('identitystore')
    
    ssoadmin_repository = SsoAdminRepository(
                sso_admin_client,
                identitystore_client
            )
    account_repository = AccountRepository(organizations_client)
    
    accounts = account_repository.get_all_accounts()
    account_user_assignments = []
    for account in accounts:
        userassignments = ssoadmin_repository.get_bindings_by_account_id(account['Id'])
        # Example Output
        # {
        #   "Id": "123456789123",
        #   "Name": "fanyaccount",
        #   "userassignments": [
        #     {
        #       "permission_set_arn": "arn:aws:sso:::permissionSet/ssoins-27348293579/ps-aa89082359dfs",
        #       "permission_set_name": "AWSReadOnlyAccess",
        #       "attached_users": [
        #         {
        #           "PrincipalType": "USER",
        #           "Id": "23a4cd82-c231-ac70-b5f5-791ae20f974c",
        #           "Name": "fancyuser"
        #         }
        #       ]
        #     }
        #   ]
        # }
        account_user_assignments.append({
            **account,
            'userassignments': userassignments
        })
    
    for account_assignments in account_user_assignments:
        print (account_assignments)