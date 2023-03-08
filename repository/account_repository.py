import itertools
import logging

class AccountRepository:
    def __init__(self, boto3_organizations_client):
        """
        Example:
            account_repository = AccountRepository(
                boto3.client('organizations')
            )
        """
        self._organizations_client = boto3_organizations_client
        self.active_accounts = self._load_active_accounts()
    
    def get_all_account_ids(self):
        return [account['Id'] for account in self.active_accounts]

    def get_all_accounts(self):
        """
        Returns
        -------
        accounts : list(dict)
          example: [
            {
              'Id': '696969696969', 
              'Name': 'secretaccount'
            }
          ]
        """
        return [{ 'Id': account['Id'], 'Name': account['Name'] }  for account in self.active_accounts]
    
    def get_accountname_by_id(self, account_id:str) -> str:
        return next((account['Name'] for account in self.active_accounts if account['Id'] == account_id),None)
    
    def _load_active_accounts(self):
        """Retrieves all account in your organization.
    
        Must be called within the management account where the organization is configured.
            
        Returns
        -------
        accounts : list(str)
            
        Raises
        ------
        Organizations.Client.exceptions.AccessDeniedException
        Organizations.Client.exceptions.AWSOrganizationsNotInUseException
        Organizations.Client.exceptions.InvalidInputException
        Organizations.Client.exceptions.ServiceException
        Organizations.Client.exceptions.TooManyRequestsException
        
        
        References
        ----------
        .. [1] "Boto3 Endpoint", https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations/client/list_accounts.html
        """
        if hasattr(self,'active_accounts'):
            return self.active_accounts
        paginator =  self._organizations_client.get_paginator('list_accounts')
        logging.info(f'Loading all active account with organizations:ListAccounts API call')
        account_page_iterator = paginator.paginate(MaxResults=20)
        # Returns
        # [
        #     {
        #         'Id': 'string',
        #         'Arn': 'string',
        #         'Email': 'string',
        #         'Name': 'string',
        #         'Status': 'ACTIVE'|'SUSPENDED'|'PENDING_CLOSURE',
        #         'JoinedMethod': 'INVITED'|'CREATED',
        #         'JoinedTimestamp': datetime(2015, 1, 1)
        #     }
        # ]
        accounts = list(
            itertools.chain(
                *[account_page['Accounts'] for account_page in account_page_iterator]
                ))
        self.active_accounts =  [account for account in accounts if account['Status'] == 'ACTIVE']
        return self.active_accounts
        