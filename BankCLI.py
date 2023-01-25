import sys
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker

from Transactions import Base
from Bank import Bank
from Accounts import OverdrawError, TransactionLimitError, TransactionSequenceError

logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class BankCLI():
    def __init__(self):
        self._session = Session()

        #get bank from db
        self._bank = self._session.query(Bank).first()

        #if bank does not exist then initialize and save a new bank
        if self._bank:
            logging.debug("Loaded from bank.db")     
        else:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")       
        self._selected_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._list_transactions,
            "5": self._add_transaction,
            "6": self._monthly_triggers,
            "7": self._quit,
        }

    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: list transactions
5: add transaction
6: interest and fees
7: quit"""
        )

    def run(self):
        """Display the menu and respond to choices."""

        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def _summary(self):
        for x in self._bank.show_accounts():
            print(x)

    def _quit(self):
        sys.exit(0)

    def _add_transaction(self):
        amount = None
        while amount == None:
            try:
                amount = Decimal(input("Amount?\n>"))
            except InvalidOperation:
                print("Please try again with a valid dollar amount.")

        date = None
        while not date:
            try:
                date = datetime.strptime(
                    input("Date? (YYYY-MM-DD)\n>"), "%Y-%m-%d").date()
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")

        try:
            self._selected_account.add_transaction(amount, self._session, date)
            self._session.commit()
            logging.debug("Saved to bank.db")
        except AttributeError:
           print("This command requires that you first select an account.")
        except OverdrawError:
            print(
                "This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError:
            print(
                "This transaction could not be completed because the account has reached a transaction limit.")
        except TransactionSequenceError as e:
            print(f"New transactions must be from {e.latest_date} onward.")

    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        amt = None
        while amt == None:
            initial_deposit = input("Initial deposit amount?\n>")
            try:
                amt = Decimal(initial_deposit)
            except InvalidOperation:
                print("Please try again with a valid dollar amount.")
        try:
            self._bank.add_account(acct_type, amt, self._session)
            self._session.commit()
            logging.debug("Saved to bank.db")
        except OverdrawError:
            print(
                "This transaction could not be completed due to an insufficient account balance.")

    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthly_triggers(self):
        try:
            self._selected_account.assess_interest_and_fees(self._session)
            self._session.commit()
            logging.debug("Triggered fees and interest")
            logging.debug("Saved to bank.db")
        except AttributeError:
            print("This command requires that you first select an account.")
        except TransactionSequenceError as e:
            print(
                f"Cannot apply interest and fees again in the month of {e.latest_date.strftime('%B')}.")

    def _list_transactions(self):
        try:
            for x in self._selected_account.get_transactions():
                print(x)
        except AttributeError:
            print("This command requires that you first select an account.")


if __name__ == "__main__":

    engine = sqlalchemy.create_engine("sqlite:///bank.db")
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)
    
    try:
        BankCLI().run()
    except Exception as e:
        print("Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.")
        logging.error(str(e.__class__.__name__) + ": " + repr(str(e)))
