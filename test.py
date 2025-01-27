
from tkinter import *
from tkinter import ttk, StringVar, CENTER, TOP
from tkinter.messagebox import askyesno

import os


root = Tk()
root.title("Music Player")
root.geometry("800x600")
# Setup frame for layout
frm = ttk.Frame(root, padding=10)
frm.pack(fill='both', expand=True)
root.mainloop()
#ttk.OptionMenu()
