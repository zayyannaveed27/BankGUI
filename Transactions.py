from datetime import datetime, date, timedelta
import logging
from decimal import Decimal, setcontext, BasicContext
import functools
from sqlalchemy import Column,Float, Integer, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# context with ROUND_HALF_UP
setcontext(BasicContext)


@functools.total_ordering
class Transaction(Base):

    __tablename__ = "transaction"
    _id = Column(Integer, primary_key = "True")
    _amt = Column(Float(asdecimal=True))
    _account_id = Column(Integer, ForeignKey("account._id"))
    _date = Column(Date)
    _exempt = Column(Boolean)

    def __init__(self, amt, acct_num, date=None, exempt=False):
        """
        Args:
            amt (Decimal): Decimal object representing dollar amount of the transaction.
            acct_num (int): Account number used for logging the transaction's creation.
            date (Date, optional): Date object representing the date the transaction was created.Defaults to None.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """
        self._amt = amt
        self._date = date
        if not self._date:
            self._date = datetime.now().date()
        self._exempt = exempt
        logging.debug(f"Created transaction: {acct_num}, {self._amt}")

    @property
    def date(self):
        # exposes the date as a read-only property to facilitate new
        # functionality in Account
        return self._date
    
    @property
    def amt(self):
        # exposes the date as a read-only property to facilitate new
        # functionality in GUI
        return self._amt

    def __str__(self):
        """Formats the date and amount of this transaction
        For example, 2022-9-15, $50.00'
        """ 
        return f"{self._date}, ${self._amt:,.2f}"

    def is_exempt(self):
        "Check if the transaction is exempt from account limits"
        return self._exempt

    def in_same_day(self, other):
        "Takes in a date object and checks whether this transaction shares the same date"
        return self._date == other._date

    def in_same_month(self, other):
        "Takes in a date object and checks whether this transaction shares the same month and year"
        return self._date.month == other._date.month and self._date.year == other._date.year

    def __radd__(self, other):
        "Adds Transactions by their amounts"

        # allows us to use sum() with transactions
        return other + self._amt

    def check_balance(self, balance):
        "Takes in an amount and checks whether this transaction would withdraw more than that amount"

        return self._amt >= 0 or balance >= abs(self._amt)

    def __lt__(self, other):
        return self._date < other._date

    def __eq__(self, other):
        return self._date == other._date

    def last_day_of_month(self):
        """ Returns the last day of the month that this transaction is in"""
        # Creates a date on the first of the next month (being careful about
        # wrapping around to January) and then subtracts one day
        return date(self._date.year + self._date.month // 12,
                    self._date.month % 12 + 1, 1) - timedelta(1)
