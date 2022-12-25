from tkinter import *
from tkinter import filedialog, messagebox, ttk
from sic import Sic
from sicxe import SicXE


class App:
    def __init__(self, master) -> None:
        self.menu = None
        self.master = master
        label_frame1 = LabelFrame(master, text="LOADER-LINKER PROJECT", font=("Arial", 25))
        label_frame1.pack(pady=150, padx=150)
        Label(label_frame1, text="Choose SIC or SIC-XE").pack(side=TOP)
        self.radio = StringVar()
        R1 = Radiobutton(label_frame1, text="SIC", variable=self.radio, value="sic", command=self.handleSelect)
        R1.pack(anchor=CENTER)
        R2 = Radiobutton(label_frame1, text="SIC-XE", variable=self.radio, value="sicxe", command=self.handleSelect)
        R2.pack(anchor=CENTER)

    def handleSelect(self):
        selection = self.radio.get()
        if selection == "sic":
            sic = Sic(self.menu)
        if selection == "sicxe":
            sic_xe = SicXE()
