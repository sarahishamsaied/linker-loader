from tkinter import *
from tkinter import filedialog
import numpy as np
import pandas as pd
from pandastable import Table


class Sic:
    def __init__(self, master) -> None:
        self.arr = []
        self.addresses = []
        self.lengths = []
        self.tRecs = ""
        self.df = None
        self.filepath = ""
        menu = Tk()
        menu.geometry("900x500")
        menu.title("Absolute Loader")
        labelframe = LabelFrame(menu, text="GENERATE ABSOLUTE LOADER FROM SIC PROGRAM", font=("Arial", 16), padx=50,
                                pady=50)
        labelframe.pack()
        Label(labelframe, text="Import HTE file .txt").pack()
        button = Button(labelframe, text="Browse a file", command=self.openfile)
        button.pack()
        menu.mainloop()

    def openfile(self):
        file = filedialog.askopenfile(mode="r", filetypes=[("Text Files", "*.txt")])
        self.filepath = file.name
        if file:
            self.read_hte_file()
            self.generate_memory()
            self.load_data()
            self.generate_table()

    def read_hte_file(self):
        hte_rec = open(self.filepath, "r")
        for line in hte_rec:
            if line[0] == 'T':
                print(line)
                self.addresses.append(line[1:7])
                self.lengths.append(line[7:9])
                self.tRecs += line[9:].strip()
        arr = [self.tRecs[i:i + 2] for i in range(0, len(self.tRecs), 2)]
        self.arr = np.array(arr)

    def generate_memory(self):
        """
        Creates a dataframe object filled with zeros.

        * **mem_addresses** : is a numpy array of integer addresses that should be
        * in the table, starts from address[0] and ends at nine rows after the last address

        * **convert_address_to_hex** : a function that converts values in the `mem_addresses` array to hexadecimal

        * **format_hex_addresses** : a function that formats hexadecimal values in the addresses array by removing "0x"

        * **mem** : the generated 2D zero-valued numpy array
        :rtype: None
        """
        min_address = min(self.addresses)[:5] + "0"
        max_address = max(self.addresses)[:5] + "0"
        mem_addresses = np.arange(int(min_address, 16), int(max_address, 16) + 16 * 5, 16)

        def format_hex_addresses(x): return hex(x).replace("0x", "").zfill(6).upper()

        mem_hex_addresses = np.array([format_hex_addresses(x) for x in mem_addresses])  # [001000 - 002080]
        mem = np.zeros((len(mem_hex_addresses), 16), dtype=int)
        mem.astype(str)
        self.df = pd.DataFrame(np.zeros((len(mem_addresses), 16)), index=mem_hex_addresses, columns=np.arange(0, 16))
        self.df = self.df.astype(str)

    def load_data(self):
        i = 0
        for address, length in zip(self.addresses, self.lengths):
            end_address = (int(address, 16) + int(length, 16)) - 1
            current = int(address[0:5] + "0", 16)
            col = int(address[5], 16)
            add = int(address.upper(), 16)
            while add < end_address:
                if col == 16:
                    col = 0
                    current = current + 16
                row = hex(current).replace("0x", "").zfill(6)
                add = int(row[:len(row) - 1] + hex(col).replace("0x", "").upper(), 16)
                self.df.at[row, col] = self.arr[i].upper()
                i += 1
                col += 1
        print(self.df)

    def generate_table(self):
        # self.df.to_csv("output.csv", encoding=None)
        root = Tk()
        root.geometry("600x500")
        root.title("Absolute Loader Example")
        frame = Frame(root)
        frame.pack(fill="both", expand=True)
        table = Table(frame, dataframe=self.df, width=500, maxcellwidth=30)
        table.show()
        table.showindex = True
        root.mainloop()
