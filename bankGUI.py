import sys
import logging
from decimal import Decimal, InvalidOperation
from datetime import datetime
from turtle import bgcolor, width
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
from Transactions import Base
from Bank import Bank
from Accounts import OverdrawError, TransactionLimitError, TransactionSequenceError
from megawidgets import TransactionGrid
import tkinter as tk
from tkinter import DISABLED, messagebox
from tkinter import ttk
from tkcalendar import Calendar

# define a callback function that handles exceptions
def handle_exception(exception, value, traceback):
    messagebox.showwarning('Unhandled Exception', "Sorry! Something unexpected happened. If this problem persists please contact our support team for assistance.")
    logging.error(f"{exception.__name__}: {repr(value)}")
    sys.exit(1)

logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class BankGUI():
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

        #store account and transaction buttons in lists
        self._account_list = []
        self._transaction_list = []
        
        #create a root with title Bank
        self._window = tk.Tk()

        # register the callback on the tk window
        self._window.report_callback_exception = handle_exception 
        
        #personalized window style method
        self._window_style()

        #create options frame
        self._create_options_frame()

        #create separate frames for display accounts, opening account and listing transactions
        self._open_account_frame = tk.Frame(self._window)
        self._summary_frame = tk.Frame(self._window)
        self._list_transactions_frame = tk.Frame(self._window)
        self._add_transaction_frame = tk.Frame(self._window,)
       
        #use style theme for calender in adding transaction
        style = ttk.Style(self._add_transaction_frame)
        style.theme_use('clam')

        #place the frames in GUI    
        self._summary_frame.grid(row=2, column=0, sticky="nsew")
        self._list_transactions_frame.grid(row=2, column=1, sticky="nsew")
        self._list_transactions_frame.tkraise()
        
        #create megawidget for displaying transactions
        self._trans_grid = TransactionGrid(self._list_transactions_frame, self._transaction_list)

        self._summary()
        self._window.mainloop()

    #style the main root window
    def _window_style(self):

        self._window.title("Bank of OOP")    
        self._window.geometry('700x500')
        window_style = ttk.Style(self._window)
        window_style.theme_use('aqua')

        self._window.grid_rowconfigure(2, weight=1)
        self._window.grid_columnconfigure(0, uniform="half", weight=1)
        self._window.grid_columnconfigure(1, uniform="half", weight=1)
        
    def _create_options_frame(self):
        #create a frame for menu options
        self._options_frame = tk.Frame(self._window,)
        self._options_frame.grid(row = 0, column = 0, columnspan= 6)

        #create buttons for add account, add transaction and interest and fees
        self._open_acc_btn = tk.Button(self._options_frame, text="Open Account", width= 18, activebackground='blue',
                                    command=self._open_account_gui ).pack( padx=5, pady=15, side=tk.LEFT)
        self._add_transc_btn = tk.Button(self._options_frame, text="Add Transaction", width= 18, state = tk.NORMAL,
                                    command=self._add_transaction_gui)
        self._add_transc_btn.pack(padx=5, pady=15, side=tk.LEFT)
        self._monthly_trig_btn = tk.Button(self._options_frame, text="Interest and Fees", width= 18,
                                    command=self._monthly_triggers).pack(padx=5, pady=15, side=tk.LEFT)
    

    #method to display widgets for adding transaction
    def _add_transaction_gui(self):

        #disable add transaction button
        self._add_transc_btn['state'] = tk.DISABLED

        #check if any account is selected
        if self._selected_account == None:
            self._add_transc_btn['state'] = tk.NORMAL
            messagebox.showwarning('Account not Selected', "This command requires that you first select an account.")
            return

        #display frame
        self._add_transaction_frame.grid(row=1, column=1, sticky="nsew")

        #check validity of amount
        def validation_check():
            try:
                amount = Decimal(e1.get())
            except InvalidOperation:
                messagebox.showwarning('Invalid Decimal', 'Please try again with a valid dollar amount.')
            else:
                add_callback(amount)
                

        #callback for add account enter button
        def add_callback(amount):
            date = datetime.strptime(calender.get_date(), "%m/%d/%y").date()
            self._add_transaction(amount, date)
            e1.destroy()
            b1.destroy()
            l1.destroy()
            l2.destroy()
            calender.destroy()
            self._add_transaction_frame.grid_forget()
            self._list_transactions()
            self._summary()
            self._add_transc_btn['state'] = tk.NORMAL


        #label for amount
        l1 = tk.Label(self._add_transaction_frame, text="Deposit Amount:")
        l1.pack()

        #entry for getting amount
        e1 = tk.Entry(self._add_transaction_frame, width= 15)

        #dynamic fg changing function for entry
        def input_color(arg):
            if len(e1.get()) > 0:
                try:
                    float(e1.get())
                except ValueError:
                    e1.configure(foreground = 'red')
                else:
                    e1.configure(foreground = 'green')
            return      
        e1.bind('<KeyRelease>', input_color)
        e1.pack() 

        #label for transaction date calender
        l2 = tk.Label(self._add_transaction_frame, text="Date:", font= "Arial 12" )
        l2.pack()

        #calender for date input
        calender_date = datetime.today()
        if self._selected_account.get_transactions():
            calender_date = max(self._selected_account.get_transactions()).date
        calender = Calendar(self._add_transaction_frame, selectmode='day', locale='en_US',
                    month=calender_date.month, day=calender_date.day, year=calender_date.year)
        calender.pack()

        #entry button
        b1 = tk.Button(self._add_transaction_frame, text="Enter", command = validation_check)
        b1.pack()
    
    #method to process GUI input for adding transaction
    def _add_transaction(self, amount, date):
        try:
            self._selected_account.add_transaction(amount, self._session, date)
            self._session.commit()
            logging.debug("Saved to bank.db")

        except OverdrawError:
            messagebox.showwarning('Insufficient Balance', 
                "This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError:
            messagebox.showwarning('Transaction Limit reached',
                "This transaction could not be completed because the account has reached a transaction limit.")
        except TransactionSequenceError as e:
            messagebox.showwarning('Invalid Date',
            f"New transactions must be from {e.latest_date} onward.")


     #method to display widgets for opening account
    def _open_account_gui(self):

        self._open_account_frame.grid(row=1, column=0)
        
        #validate entry amount as decimal
        def validate_amount():
            try:
                amount = Decimal(e1.get())
            except InvalidOperation:
                messagebox.showwarning('Account Creation Failed', 'Please try again with a valid dollar amount.')
            else:
                add_callback(amount)

        #callback for add account enter button
        def add_callback(amount):
            self._open_account(clicked.get(), amount)
            e1.destroy()
            b1.destroy()
            l1.destroy()
            l2.destroy()
            type_drop.destroy()
            self._open_account_frame.grid_forget()
            self._summary()

        #label for dropdown account type
        l1 = tk.Label(self._open_account_frame, text="Type of account:")
        l1.grid(row = 0, column = 0, padx = (3,0))

         # Creat Dropdown menu for account type
        options = [ "savings", "checking"]
        clicked = tk.StringVar()
        clicked.set( "savings" )
        type_drop = tk.OptionMenu( self._open_account_frame , clicked , *options )
        type_drop.grid(row = 0, column = 1)
        
        #label for amount
        l2 = tk.Label(self._open_account_frame, text="Initial deposit:")
        l2.grid(row = 1, column = 0)

        #entry for getting amount
        e1 = tk.Entry(self._open_account_frame, width= 15)

        #dynamic fg changing function for entry
        def input_color(arg):
            if len(e1.get()) > 0:
                try:
                    float(e1.get())
                except ValueError:
                    e1.configure(foreground = 'red')
                else:
                    e1.configure(foreground = 'green')
            return      

        e1.bind('<KeyRelease>', input_color)
        e1.grid(row=1, column=1)

        #entry button
        b1 = tk.Button(self._open_account_frame, text="Enter", command = validate_amount)
        b1.grid(row=0, column=2, rowspan= 2)

    def _open_account(self, acct_type, amt):

        try:
            self._bank.add_account(acct_type, amt, self._session)
            self._session.commit()
            logging.debug("Saved to bank.db")
        except OverdrawError:
            messagebox.showwarning('Account Creation Failed', 'This transaction could not be completed due to an insufficient account balance.')

    def _select(self, num):
        self._selected_account = self._bank.get_account(num)
        self._list_transactions()

    def _list_transactions(self):

        self._trans_grid.destroyer()

        t = self._selected_account.get_transactions()
        self._list_transactions_frame.tkraise()
        self._trans_grid = TransactionGrid(self._list_transactions_frame, t)

    #process interest and fees from the monthly triggers button
    def _monthly_triggers(self):
        try:
            self._selected_account.assess_interest_and_fees(self._session)
            self._session.commit()
            logging.debug("Triggered fees and interest")
            logging.debug("Saved to bank.db")
        except AttributeError:
            messagebox.showwarning('Account not selected', 'This command requires that you first select an account.')
        except TransactionSequenceError as e:
            messagebox.showwarning('Interest already applied', f"Cannot apply interest and fees again in the month of {e.latest_date.strftime('%B')}.")
        else:
            self._list_transactions()
            self._summary()

    #display accounts in GUI            
    def _summary(self):

        for x in self._account_list:
            x.destroy()
        
        for x in self._bank.show_accounts():
            acc_btn = tk.Radiobutton(self._summary_frame, text = x, 
                        command=lambda num = x._account_number: self._select(num),
                        value = x._account_number, indicator = 0, width = 30,
                        background = "light blue", activebackground ='white')
            acc_btn.pack(fill = tk.X, ipady = 5, padx = 5)
            self._account_list.append(acc_btn)


if __name__ == "__main__":

    engine = sqlalchemy.create_engine("sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    BankGUI()