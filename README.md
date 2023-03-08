# AWS Identity Center: Retrieve Account Assignments

A simple script to retrieve account assignments.

## Test the solution

Assign the correct AWS profile for Boto3 in get_users.py.
Run the script get_users.py against your management account. Needed access Rights are documented below.

## Class Diagramm
IMPORTANT: You can control wether you want to retrieve only Users, Groups or both with the principal_type attribute in get_bindings_by_account_id.
           Allowed principal_types are 'USER', 'GROUP', 'ALL'. Defaults to 'USER'
 
 ![image](https://user-images.githubusercontent.com/10559693/223778777-d234dcfa-6bae-41db-8053-183126b6636f.png)

 ┌──────────────────────────────────────────────────────────────────────────────────┐            ┌────────────────────────────────────────────────┐
 │ SsoAdminRepository                                                               │     ┌──────┤ IdentitystoreRepository                        │
 │                                                                                  │     │      │                                                │
 │   -_ssoadmin_client:boto3.client                                                 │     │      │   -_identitystore_client:boto3:client          │
 │                                                                                  │     │      │                                                │
 │   +instance_arn:str                                                              │     │      │   +identitystore_id                            │
 │                                                                                  │     │      │                                                │
 │   +identitystore_id:str                                                          │     │      │   +user_repository:dict                        │
 │                                                                                  │     │      │                                                │
 │   +identitystore_repository:IdentitystoreRepository                              ├─────┘      │   +group_repository:dict                       │
 │                                                                                  │            ├────────────────────────────────────────────────┤
 │   +permissionsets                                                                │            │                                                │
 ├──────────────────────────────────────────────────────────────────────────────────┤            │   +get_username_by_id(user_id:str)             │
 │                                                                                  │            │                                                │
 │   -_get_first_instance()                                                         │            │   +get_groupname_by_id(group_id:str)           │
 │                                                                                  │            │                                                │
 │   -_get_account_ids_by_permissionset(permission_set_arn)                         │            └────────────────────────────────────────────────┘
 │                                                                                  │
 │   -_get_bindings_by_permissionset(account_id, permission_set_arn, princpal_type  │            ┌─────────────────────────────────────────┐
 │                                                                                  │            │ AccountRepository                       │
 │   -_get_userbindings_by_permissionset(all_account_assignments)                   │            │                                         │
 │                                                                                  │            │   -_organizations_client:boto3.client   │
 │   -_get_groupbindings_by_permissionset(all_account_assignments)                  │            │                                         │
 │                                                                                  │            │   +active_accounts:dict                 │
 │   +load_all_permissionsets()                                                     │            ├─────────────────────────────────────────┤
 │                                                                                  │            │                                         │
 │   +get_bindings_by_account_id(account_id, principal_type)                        │            │   +get_accountname_by_id(account_id:str)│
 │                                                                                  │            │                                         │
 └──────────────────────────────────────────────────────────────────────────────────┘            │   -_load_active_accounts()              │
                                                                                                 │                                         │
                                                                                                 └─────────────────────────────────────────┘
                                                                                                 
## Needed Access Rights

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GetAllSSOAccountAssignments",
            "Effect": "Allow",
            "Action": [
                "organizations:ListAccounts",
                "identitystore:DescribeUser",
                "identitystore:DescribeGroup",
                "sso:ListInstances",
                "sso:ListPermissionSets",
                "sso:ListAccountsForProvisionedPermissionSet",
                "sso:DescribePermissionSet",
                "sso:ListAccountAssignments"
            ],
            "Resource": "*"
        }
    ]
}
