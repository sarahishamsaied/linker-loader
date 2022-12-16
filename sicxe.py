import tkinter
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd
from pandastable import Table


def to_hex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


class SicXE:
    def __init__(self) -> None:
        self.control_sections = None
        self.labelsDf = None
        self.estab = {}
        self.defs = []
        self.defs_addresses = []
        self.filepath = ""
        self.starting_address = "000000"
        self.starting_address_entry = None
        self.arr = []
        self.addresses = []
        self.lengths = []
        self.modified_rows = []
        self.modified_cols = []
        self.tRecs = ""
        self.unique_index = []
        self.df = None
        self.start = None
        self.name = None
        self.found_address = None
        self.label = None
        self.operator = None
        self.value = None
        self.colored = {}
        self.firstChar = ""
        menu = Tk()
        menu.geometry("900x500")
        menu.title("Absolute Loader")
        print("hello")
        self.labelframe = LabelFrame(menu, text="GENERATE LINKING LOADER FROM SIC-XE PROGRAM", font=("Arial", 16),
                                     padx=50, pady=50)
        self.labelframe.pack()
        Label(self.labelframe, text="Enter starting address").pack()
        self.starting_address_entry = Entry(self.labelframe)
        self.starting_address_entry.pack()
        Button(self.labelframe, text="Confirm address", command=self.setEntry).pack()
        print("star:", self.starting_address)
        Label(self.labelframe, text="Import HDRTME file .txt").pack()
        button = Button(self.labelframe, text="Browse a file", command=self.openfile)
        button.pack()
        menu.mainloop()
        self.starting_address = self.starting_address_entry.get()

    def openfile(self):
        file = filedialog.askopenfile(mode="r", filetypes=[("Text Files", "*.txt")])
        self.filepath = file.name
        self.generate_external_symbol_table()
        self.set_addresses()
        self.generate_memory()
        self.load_data()
        self.modify_data()
        self.generate_table()

    def setEntry(self):
        print("here")
        self.starting_address = self.starting_address_entry.get()

    def generate_external_symbol_table(self):
        hdrtme = open(self.filepath, "r")
        self.control_sections = []
        control_section_addresses = []
        control_section_lengths = []
        for line in hdrtme:
            if line[0] == 'H':
                name = line[1:6]
                address = hex(int(line[7:13], 16) + int(self.starting_address, 16)).replace("0x", "").zfill(6).upper()
                length = line[13:].strip()
                self.control_sections.append(name)
                control_section_addresses.append(address)
                control_section_lengths.append(length)
            if line[0] == 'D':
                line = line.strip()
                self.defs = [line[i:i + 6] for i in range(1, len(line), 12)]
                self.defs_addresses = [line[i:i + 6] for i in range(7, len(line), 12)]
                definitions = {}
                for definition, definition_address in zip(self.defs, self.defs_addresses):
                    definitions[definition.replace("X", "")] = definition_address
                self.estab[name] = {"address": address, "length": length, "definitions": definitions}
        for i in range(1, len(control_section_addresses)):
            control_section_addresses[i] = hex(
                int(control_section_addresses[i - 1], 16) + int(control_section_lengths[i - 1], 16)).replace("0x",
                                                                                                             "").zfill(
                6)
        for addr, (k, v) in zip(control_section_addresses, self.estab.items()):
            v['address'] = addr
            for dk, dv in v['definitions'].items():
                v['definitions'][dk] = hex(int(v['definitions'][dk], 16) + int(v['address'], 16)).replace("0x",
                                                                                                          "").zfill(
                    6).upper()
        self.labelsDf = pd.DataFrame.from_dict(self.estab, orient='index')
        root = Tk()
        root.geometry("600x300")
        root.title("External Symbol Table Example")
        frame = Frame(root)
        frame.pack(fill="both", expand=True)
        table = Table(frame, dataframe=self.labelsDf)
        table.show()
        table.showindex = True
        root.mainloop()

    def set_addresses(self):
        hteRec = open(self.filepath, "r")

        for line in hteRec:
            if line[0] == 'H':
                name = line[1:6]
                start = self.estab[name.replace("X", "")]['address']
            if line[0] == 'T':
                x = int(line[1:7], 16) + int(start, 16)
                print(hex(x))
                #         print(f"{line[1:7]} + {start} = {hex(x)}")
                self.addresses.append(hex(x).replace("0x", "").zfill(6).upper())
                self.lengths.append(line[7:9])
                self.tRecs += line[9:].strip()
        self.arr = [self.tRecs[i:i + 2] for i in range(0, len(self.tRecs), 2)]
        self.arr = np.array(self.arr)

    def generate_memory(self):
        min_address = min(self.addresses)[:5] + "0"
        max_address = max(self.addresses)[:5] + "0"
        mem_addresses = np.arange(int(min_address, 16), int(max_address, 16) + 32, 16)

        def convert_address_to_hex(x): return hex(x)

        def format_hex_addresses(x): return x.replace("0x", "").zfill(6).upper()

        mem_hex_addresses = np.array([convert_address_to_hex(x) for x in mem_addresses])
        mem_hex_addresses = np.array([format_hex_addresses(x) for x in mem_hex_addresses])
        mem = np.zeros((len(mem_hex_addresses), 16), dtype=int)
        mem = mem.astype(str)
        self.df = pd.DataFrame(np.zeros((len(mem_addresses), 16)), index=mem_hex_addresses, columns=np.arange(0, 16))
        self.df = self.df.astype(str)
        self.unique_index = pd.Index(mem_hex_addresses)

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
                row = hex(current).replace("0x", "").zfill(6).upper()
                add = int(row[:len(row) - 1] + hex(col).replace("0x", "").upper(), 16)
                self.df.at[row, col] = self.arr[i].upper()
                i += 1
                col += 1

    def modify_data(self):
        hteRec = open(self.filepath, "r")

        for line in hteRec:
            self.firstChar = ""
            if line[0] == 'H':
                self.name = line[1:6]
                self.start = self.estab[self.name.replace("X", "")]['address']
            if line[0] == 'M':
                z = hex(int(line[1:7], 16) + int(self.start, 16)).replace("0x", "").zfill(6).upper()
                row = z[0:5] + "0".upper()
                col = int(z[5:6], 16)
                length = line[7:9]
                self.operator = line[9:10]
                self.label = line[10:].strip()
                if col < 14:
                    if self.unique_index.get_loc(row) in self.colored:
                        self.colored[self.unique_index.get_loc(row)].extend([col, col + 1, col + 2])
                    else:
                        self.colored[self.unique_index.get_loc(row)] = [col, col + 1, col + 2]
                    self.value = str(self.df.loc[row, col]) + str(self.df.loc[row, col + 1]) + str(
                        self.df.loc[row, col + 2])
                elif col == 14:
                    if self.unique_index.get_loc(row) in self.colored:
                        self.colored[self.unique_index.get_loc(row)].extend([col, col + 1])
                    else:
                        self.colored[self.unique_index.get_loc(row)] = [col, col + 1]
                    self.colored[
                        self.unique_index.get_loc(hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper())] = [0]
                    self.value = str(self.df.loc[row, col]) + str(self.df.loc[row, col + 1]) + str(
                        self.self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 0])
                elif col == 15:
                    if self.unique_index.get_loc(row) in self.colored:
                        self.colored[self.unique_index.get_loc(row)].extend([col])
                    else:
                        self.colored[self.unique_index.get_loc(row)] = [col]
                    self.colored[
                        self.unique_index.get_loc(hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper())] = [0, 1]
                    self.value = str(self.df.loc[row, col]) + str(
                        self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 0]) + str(
                        self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 1])
                if length == '05':
                    self.firstChar = self.value[0]
                    self.value = self.value[1:]
                for k, v in self.estab.items():
                    if k == self.label:
                        self.found_address = self.estab[k]['address']
                        break
                    for dk, dv in v['definitions'].items():
                        if dk == self.label:
                            self.found_address = dv
                            break
                if self.operator == "+":
                    self.value = self.firstChar + hex(int(self.value, 16) + int(self.found_address, 16)).replace("0x",
                                                                                                                 "").zfill(
                        6).upper()[-int(length):]
                if self.operator == "-":
                    y = int(self.value, 16) - int(self.found_address, 16)
                    self.value = self.firstChar + to_hex(y, 32).replace("0x", "").zfill(6).upper()[-int(length):]
                if col < 14:
                    self.df.at[row, col] = self.value[0:2]
                    self.df.at[row, col + 1] = self.value[2:4]
                    self.df.at[row, col + 2] = self.value[4:6]
                if col == 14:
                    self.df.at[row, col] = self.value[0:2]
                    self.df.at[row, col + 1] = self.value[2:4]
                    self.df.at[hex(int(row, 16).replace("0x", "").zfill(6).upper() + 16), 0] = self.value[4:6]
                if col == 15:
                    self.df.at[row, col] = self.value[0:2]
                    self.df.at[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 0] = self.value[2:4]
                    self.df.at[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 1] = self.value[4:6]
        print(self.df)

    def generate_table(self):
        # self.df.to_csv("output.csv", encoding=None)
        root = Tk()
        root.geometry("600x500")
        root.title("Linker")
        frame = Frame(root)
        frame.pack(fill="both", expand=True)
        table = Table(frame, dataframe=self.df, width=500, maxcellwidth=30)
        table.show()
        table.showindex = True
        for k, v in self.colored.items():
            print(k,v)
            table.setRowColors(rows=[k], cols=v, clr='#ADD8E6')
        root.mainloop()
