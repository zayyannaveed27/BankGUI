# Bank GUI Application README

## Introduction

This is a GUI application for a bank written in Python. The application provides a graphical user interface to interact with a bank, allowing users to open accounts, add transactions, and apply interest and fees to savings and checking accounts.

## Requirements

The following packages are required to run the Bank GUI application:

- Python (version 3.x)
- Tkinter: The standard Python interface to the Tk GUI toolkit.
- SQLAlchemy: A SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- tkcalendar: A date picker widget for Tkinter.

You can install these packages using the following command (you may also want to use a virtual environment):

```
pip install sqlalchemy tkcalendar
```

## Usage

1. To run the Bank GUI application, execute the `BankGUI.py` script using Python.

```
python BankGUI.py
```

2. The application will open a window displaying various options.

3. You can use the following buttons to interact with the bank:

   - **Open Account**: This button allows you to open a new bank account. Choose the account type (savings or checking) and the initial deposit amount.

   - **Add Transaction**: Use this button to add a transaction to an existing bank account. First, select an account from the list of displayed accounts. Then, enter the transaction amount and select the transaction date using the calendar. The application will show a warning if there is an insufficient account balance or if the account has reached the transaction limit.

   - **Interest and Fees**: This button applies the interest and fees to the selected account. A warning will be shown if you haven't selected an account or the interest and fees have already been applied for the current month.

4. The application displays the list of existing accounts, their account numbers, and current balances.

5. You can select an account by clicking on its entry in the account list. Once selected, the transactions for that account will be shown in the adjacent panel.

## Exception Handling

The application uses exception handling to catch errors and display relevant warnings to the user. If an unexpected exception occurs, the application shows a warning message and logs the error in the `bank.log` file.

## Database

The Bank GUI application uses SQLite to store data. The database file is named `bank.db` and will be created in the same directory where the application is run. The database includes tables for `bank`, `account`, and `transaction` entities.

## Limitations

- The GUI application does not support user authentication or multiple user accounts; it is meant for demonstration and learning purposes only.
- The application doesn't provide any functionality to delete accounts or transactions.
- The interest and fees calculation logic is provided as a placeholder and can be customized according to the bank's specific requirements.
- The GUI may not handle all edge cases and exceptional scenarios; it is recommended to test the application thoroughly.

## Contributing

Contributions to this project are welcome! If you find any issues or have ideas for improvements, feel free to open an issue or submit a pull request.

## Author

Zayyan Naveed

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
---
