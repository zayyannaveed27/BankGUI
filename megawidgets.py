import tkinter as tk

class TransactionGrid(tk.Frame):
    """ A custom megawidget that is associated with Transactions in an Account """
    def __init__(self, parent, transaction_list, **kwargs):
        super().__init__(parent, **kwargs) 
        self._transaction_list = transaction_list
        self._labels = []

        #create list of transaction labels
        for t in self._transaction_list:
            #red for withdrawal and green for deposit
            if t.amt >= 0:
                color = 'green'
            else:
                color = 'red'
            l = tk.Label(parent, text=str(t), width= 27, relief=tk.SUNKEN, fg = color)
            l.pack( padx=5)
            self._labels.append(l)

    def destroyer(self):
        """Method to destroy the megawidget"""
        for x in self._labels:
            x.destroy()
        
