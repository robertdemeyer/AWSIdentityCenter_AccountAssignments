import itertools
import logging
from repository.identitystore_repository import IdentitystoreRepository

class SsoAdminRepository:
    def __init__(self, boto3_ssoadmin_client, boto3_identitystore_client, sso_admin_instance=None):
        '''
        Example:
            sso_admin_client = boto3.client('sso-admin')
            identitystore_client = boto3.client('identitystore')
            instance = sso_admin_client.list_instances().get('Instances',[{'InstanceArn':'','IdentityStoreId':''}])[0]
            ssoadmin_repository = SsoAdminRepository(
                sso_admin_client,
                identitystore_client,
                instance
            )
        '''
        self._ssoadmin_client = boto3_ssoadmin_client
        if not sso_admin_instance:
            sso_admin_instance = self._get_first_instance()
        self.instance_arn = sso_admin_instance['InstanceArn']
        self.identitystore_id = sso_admin_instance['IdentityStoreId']
        self.identitystore_repository = IdentitystoreRepository(
                boto3_identitystore_client,
                self.identitystore_id
            )
        self.permissionsets = []
        
    def _get_first_instance(self):
        """Initializes the SSO Instance with the first Instance found
    
        Must be called in the account where SSO is running.
        throws an SSOAdmin.Client.exceptions.AccessDeniedException if SSO is not enabled on the account
        
        Returns
        -------
        instance : dict
          {
            'InstanceArn': 'string',
            'IdentityStoreId': 'string'
          }
            
        Raises
        ------
        SSOAdmin.Client.exceptions.InternalServerException
        SSOAdmin.Client.exceptions.ThrottlingException
        SSOAdmin.Client.exceptions.AccessDeniedException
        SSOAdmin.Client.exceptions.ValidationException
        
        
        References
        ----------
        .. [1] "Boto3 Endpoint", https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_instances.html
        """
        # {
        #     'Instances': [
        #         {
        #             'InstanceArn': 'string',
        #             'IdentityStoreId': 'string'
        #         },
        #     ],
        #     'NextToken': 'string'
        # }
        instances = self._ssoadmin_client.list_instances()
        return instances.get('Instances',[{'InstanceArn':''}])[0]
    
    def load_all_permissionsets(self):
        """Initializes all permissionsets into the local state
        
        Returns
        -------
        instance : dict
          {
            'AccountIds': ['string']
            [{
              'PermissionSet': {
                'Name': 'string',
                'PermissionSetArn': 'string',
                'Description': 'string',
                'CreatedDate': datetime(2015, 1, 1),
                'SessionDuration': 'string',
                'RelayState': 'string'
              }
            }]
          }
            
        Raises
        ------
        SSOAdmin.Client.exceptions.ResourceNotFoundException
        SSOAdmin.Client.exceptions.InternalServerException
        SSOAdmin.Client.exceptions.ThrottlingException
        SSOAdmin.Client.exceptions.ValidationException
        SSOAdmin.Client.exceptions.AccessDeniedException
        
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_permission_set.html
        """
        paginator =  self._ssoadmin_client.get_paginator('list_permission_sets')
        list_permission_sets_parameters = {
            'InstanceArn': self.instance_arn,
            'MaxResults': 100
        }
        logging.info(f'Calling ssoadmin:ListPermissionSets API to retrieve all permissionsets')
        permissionset_page_iterator = paginator.paginate(**list_permission_sets_parameters)
        permission_set_arns = list(itertools.chain(
            *[permissionset_page['PermissionSets'] for permissionset_page in permissionset_page_iterator]
            ))
        
        for permission_set_arn in permission_set_arns:
            logging.info(f'Calling ssoadmin:DescribePermissionSet API to retrieve all information for permissionset {permission_set_arn}')
            self.permissionsets.append({
                'AccountIds': self._get_account_ids_by_permissionset(permission_set_arn),
                **self._ssoadmin_client.describe_permission_set(InstanceArn=self.instance_arn,PermissionSetArn=permission_set_arn).get('PermissionSet')
            })
        return self.permissionsets

    def _get_account_ids_by_permissionset(self, permission_set_arn):
        """Retrieves all accountid´s where the requested permission_set is linked
        
        Returns
        -------
        'AccountIds': ['string']
            
        Raises
        ------
        SSOAdmin.Client.exceptions.ResourceNotFoundException
        SSOAdmin.Client.exceptions.InternalServerException
        SSOAdmin.Client.exceptions.ThrottlingException
        SSOAdmin.Client.exceptions.ValidationException
        SSOAdmin.Client.exceptions.AccessDeniedException
        
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_accounts_for_provisioned_permission_set.html
        """
        account_ids = []
        # {
        #     'AccountIds': [
        #         'string',
        #     ],
        #     'NextToken': 'string'
        # }
        logging.info(f'Calling ssoadmin:ListAccountsForProvisionedPermissionSet API to retrieve accounts for {permission_set_arn}')
        list_accounts_for_permission_set_page = self._ssoadmin_client.list_accounts_for_provisioned_permission_set(
            InstanceArn=self.instance_arn,
            PermissionSetArn=permission_set_arn
            )
        account_ids.extend(list_accounts_for_permission_set_page['AccountIds'])
        
        while(list_accounts_for_permission_set_page.get('NextToken',False)):    # No paginator available
            logging.info(f'Calling ssoadmin:ListAccountsForProvisionedPermissionSet API again to retrieve accounts for {permission_set_arn}. Reason: Pagination active')
            list_accounts_for_permission_set_page = self._ssoadmin_client.list_accounts_for_provisioned_permission_set(
                InstanceArn=self.instance_arn,
                PermissionSetArn=permission_set_arn,
                NextToken= list_accounts_for_permission_set_page['NextToken']
                )
            account_ids.extend(list_accounts_for_permission_set_page['AccountIds'])
        return account_ids
    
    def _get_bindings_by_permissionset(self, account_id: str, permission_set_arn: str, principal_type='USER'):
        """Retrives the user ID and Name linked to an account with a specific permission_set
        Parameters
        -------
        account_id : string
        permission_set_arn: string
        principal_type : string
          Allowed values: 'USER', 'GROUP', 'ALL'
        
        Returns
        -------
        instance : dict
          [{
            'PrincipalType':'USER', 
            'Id':'string',
            'Name':'string'
          }]
            
        Raises
        ------
        SSOAdmin.Client.exceptions.ResourceNotFoundException
        SSOAdmin.Client.exceptions.InternalServerException
        SSOAdmin.Client.exceptions.ThrottlingException
        SSOAdmin.Client.exceptions.ValidationException
        SSOAdmin.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.ResourceNotFoundException
        IdentityStore.Client.exceptions.ThrottlingException
        IdentityStore.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.InternalServerException
        IdentityStore.Client.exceptions.ValidationException
        
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_account_assignments.html
        """
        if principal_type not in ['USER','GROUP','ALL']:
            raise ValueError(f'principal_type must be one of "USER", "GROUP" or "ALL". Provided value {principal_type}')
        all_account_assignments = []
        # Returns
        # {
        #     'AccountAssignments': [
        #         {
        #             'AccountId': 'string',
        #             'PermissionSetArn': 'string',
        #             'PrincipalType': 'USER'|'GROUP',
        #             'PrincipalId': 'string'
        #         },
        #     ],
        #     'NextToken': 'string'
        # }
        logging.info(f'Calling ssoadmin:ListAccountAssignments API to retrieve account assignments for permissionset {permission_set_arn} in account {account_id}')
        list_account_assignments_page = self._ssoadmin_client.list_account_assignments(
            InstanceArn= self.instance_arn,
            AccountId= account_id,
            PermissionSetArn= permission_set_arn,
            MaxResults= 100
            )
        all_account_assignments.extend(list_account_assignments_page['AccountAssignments'])
        while(list_account_assignments_page.get('NextToken',False)):    # No paginator available
            logging.info(f'Calling ssoadmin:ListAccountAssignments API again to retrieve account assignments for permissionset {permission_set_arn} in account {account_id}. Reason: Pagination active.')
            list_account_assignments_page = self._ssoadmin_client.list_account_assignments(
                InstanceArn= self.instance_arn,
                AccountId= account_id,
                PermissionSetArn= permission_set_arn,
                MaxResults= 100,
                NextToken= list_account_assignments_page['NextToken']
                )
            all_account_assignments.extend(list_account_assignments_page['AccountAssignments'])
        if principal_type=='USER':
            return self._get_userbindings_by_permissionset(all_account_assignments)
        if principal_type=='GROUP':
            return self._get_groupbindings_by_permissionset(all_account_assignments)
        if principal_type=='ALL':
            return self._get_userbindings_by_permissionset(all_account_assignments) + self._get_groupbindings_by_permissionset(all_account_assignments)
            
    
    def _get_userbindings_by_permissionset(self, all_account_assignments):
        account_user_assignments = [account_assignment for account_assignment in all_account_assignments if account_assignment['PrincipalType'] == 'USER']
        return [{
            'PrincipalType':'USER', 
            'Id':user['PrincipalId'],
            'Name':self.identitystore_repository.get_username_by_id(user['PrincipalId'])
        } for user in account_user_assignments]
    
    def _get_groupbindings_by_permissionset(self, all_account_assignments):
        account_group_assignments = [account_assignment for account_assignment in all_account_assignments if account_assignment['PrincipalType'] == 'GROUP']
        return [{
            'PrincipalType':'GROUP', 
            'Id':group['PrincipalId'],
            'Name':self.identitystore_repository.get_groupname_by_id(group['PrincipalId'])
        } for group in account_group_assignments]

    def get_bindings_by_account_id(self, account_id, pricipal_type='USER'):
        """Delivers an overview about all assigned permissionset and the users assigned to a specific account
        Parameters
        -------
        account_id : string
        principal_type : string
          Allowed values: 'USER', 'GROUP', 'ALL'
        
        Returns
        -------
        instance : dict
          [{
            'permission_set_arn':'string',
            'permission_set_name':'string',
            'attached_users': [{
              'PrincipalType':'USER', 
              'Id':'string',
              'Name':'string'
            }]
          }]
            
        Raises
        ------
        SSOAdmin.Client.exceptions.ResourceNotFoundException
        SSOAdmin.Client.exceptions.InternalServerException
        SSOAdmin.Client.exceptions.ThrottlingException
        SSOAdmin.Client.exceptions.ValidationException
        SSOAdmin.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.ResourceNotFoundException
        IdentityStore.Client.exceptions.ThrottlingException
        IdentityStore.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.InternalServerException
        IdentityStore.Client.exceptions.ValidationException
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sso-admin/client/list_account_assignments.html
        """
        if (self.permissionsets == []):
            self.load_all_permissionsets()
        userbindings = []
        active_permissionsets = [permissionset for permissionset in self.permissionsets if account_id in permissionset['AccountIds']]
        for permissionset in active_permissionsets:
            permissionset_arn = permissionset['PermissionSetArn']
            permissionset_name = permissionset['Name']
            permissionset_userbindings = self._get_bindings_by_permissionset(account_id, permissionset_arn, principal_type='USER')
            if permissionset_userbindings:
                userbindings.append({
                    'permission_set_arn':permissionset_arn,
                    'permission_set_name': permissionset_name,
                    'attached_users': permissionset_userbindings
                    })
        return userbindings
