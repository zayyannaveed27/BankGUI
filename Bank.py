from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref
import logging
from Transactions import Base
from Accounts import SavingsAccount, CheckingAccount


SAVINGS = "savings"
CHECKING = "checking"

class Bank(Base):
    """ A class that maintains a set of bank accounts"""

    __tablename__ = "bank"

    _id = Column(Integer, primary_key=True)
    _accounts = relationship("Account", backref = "bank")

    #def __init__(self):
    #    self._accounts = []

    def add_account(self, acct_type, amt, session):
        """Creates a new Account object and adds it to this bank object. The Account will be a SavingsAccount or CheckingAccount, depending on the type given.

        Args:
            type (string): "Savings" or "Checking" to indicate the type of account to create
            amt (Decimal): amount for the new transaction representing the initial deposit
        """

        acct_num = self._generate_account_number()
        if acct_type == SAVINGS:
            a = SavingsAccount(acct_num)
        elif acct_type == CHECKING:
            a = CheckingAccount(acct_num)
        else:
            return None
        self._accounts.append(a)
        a.add_transaction(amt, session)
        session.add(a)

    def _generate_account_number(self):
        return len(self._accounts) + 1

    def show_accounts(self):
        "Accessor method to return accounts"
        return self._accounts

    def get_account(self, account_num):
        """Fetches an account by its account number.

        Args:
            account_num (int): account number to seach for

        Returns:
            Account: matching account or None if not found
        """        
        for x in self._accounts:
            # could be faster using dictionary
            if x._account_number == account_num:
                return x
        return None
