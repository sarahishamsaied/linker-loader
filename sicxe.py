from tkinter import *
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd
from pandastable import Table


class SicXE:
    def __init__(self) -> None:
        self.filepath = ""
        menu = Tk()
        menu.geometry("900x500")
        menu.title("Absolute Loader")
        print("hello")
        labelframe = LabelFrame(menu, text="GENERATE LINKING LOADER FROM SIC-XE PROGRAM", font=("Arial", 16), padx=50,
                                pady=50)
        labelframe.pack()
        Label(labelframe, text="Import HDRTME file .txt").pack()
        button = Button(labelframe, text="Browse a file", command=self.openfile)
        button.pack()
        menu.mainloop()

    def openfile(self):
        file = filedialog.askopenfile(mode="r", filetypes=[("Text Files", "*.txt")])
        self.filepath = file.name
