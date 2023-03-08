# AWS Identity Center: Retrieve Account Assignments

A simple script to retrieve account assignments.

## Test the solution

Assign the correct AWS profile for Boto3 in get_users.py.
Run the script get_users.py against your management account. Needed access Rights are documented below.

## Class Diagramm
IMPORTANT: You can control wether you want to retrieve only Users, Groups or both with the principal_type attribute in get_bindings_by_account_id.
           Allowed principal_types are 'USER', 'GROUP', 'ALL'. Defaults to 'USER'
 
 ![image](https://user-images.githubusercontent.com/10559693/223778777-d234dcfa-6bae-41db-8053-183126b6636f.png)
                                                                                                 
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
