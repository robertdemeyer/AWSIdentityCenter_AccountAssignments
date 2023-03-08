import logging

class IdentitystoreRepository:
    def __init__(self, boto3_identitystore_client, identitystore_id: str):
        """
        Example:
            identitystore_repository = IdentitystoreRepository(
                boto3.client('identitystore'),
                'd-9967177d78'
            )
        """
        self._identitystore_client = boto3_identitystore_client
        self.identitystore_id = identitystore_id
        self.user_repository = {}
        self.group_repository = {}
        
    def get_username_by_id(self, user_id:str):
        """Retrieves username by id
    
        Must be called within the management account where the identitystore is configured.
        The caller must have permissions for identitystore:DescribeUser
            
        Parameters
        -------
        user_id : str
        
        Returns
        -------
        username : str
            
        Raises
        ------
        IdentityStore.Client.exceptions.ResourceNotFoundException
        IdentityStore.Client.exceptions.ThrottlingException
        IdentityStore.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.InternalServerException
        IdentityStore.Client.exceptions.ValidationException
        
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/identitystore/client/describe_user.html
        """
        if user_id not in self.user_repository.keys():
            logging.info(f'Calling identitystore:DescribeUser for user id {user_id}')
            user_object = self._identitystore_client.describe_user(IdentityStoreId=self.identitystore_id, UserId=user_id)
            self.user_repository[user_id]=user_object['UserName']
        return self.user_repository[user_id]
    
    def get_groupname_by_id(self, group_id: str):
        """Retrieves username by id
    
        Must be called within the management account where the identitystore is configured.
        The caller must have permissions for identitystore:DescribeGroup
            
        Parameters
        -------
        group_id : str
        
        Returns
        -------
        groupname : str
            
        Raises
        ------
        IdentityStore.Client.exceptions.ResourceNotFoundException
        IdentityStore.Client.exceptions.ThrottlingException
        IdentityStore.Client.exceptions.AccessDeniedException
        IdentityStore.Client.exceptions.InternalServerException
        IdentityStore.Client.exceptions.ValidationException
        
        
        References
        ----------
        .. [1] https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/identitystore/client/describe_group.html
        """
        if group_id not in self.group_repository.keys():
            logging.info(f'Calling identitystore:DescribeGroup for group id {group_id}')
            # {
            #     'GroupId': 'string',
            #     'DisplayName': 'string',
            #     'ExternalIds': [
            #         {
            #             'Issuer': 'string',
            #             'Id': 'string'
            #         },
            #     ],
            #     'Description': 'string',
            #     'IdentityStoreId': 'string'
            # }
            group_object = self._identitystore_client.describe_group(IdentityStoreId=self.identitystore_id, GroupId=group_id)
            self.group_repository[group_id]=group_object['DisplayName']
        return self.group_repository[group_id]
        
    
    