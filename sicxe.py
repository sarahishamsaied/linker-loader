import tkinter
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import numpy as np
import pandas as pd
from pandastable import Table


def to_hex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))


def search_estab(estab, label):
    found_address = ""
    for k, v in estab.items():
        if k == label:
            found_address = estab[k]['address']
            break
        for dk, dv in v['definitions'].items():
            if dk == label:
                found_address = dv
                break
    return found_address


def modify_cell(operator, first_char, cell_val, length, found_address):
    if operator == "+":
        value = first_char + hex(int(cell_val, 16) + int(found_address, 16)).replace("0x",
                                                                                     "").zfill(
            6).upper()[-int(length):]
    if operator == "-":
        y = int(cell_val, 16) - int(found_address, 16)
        value = first_char + to_hex(y, 32).replace("0x", "").zfill(6).upper()[-int(length):]
    return value


def return_modified_positions(row, col):
    positions = {"modified_rows": [], "modified_cols": []}
    if col < 14:
        positions["modified_rows"].extend([row, row, row])
        positions["modified_cols"].extend([col, col + 1, col + 2])

    if col == 14:
        positions["modified_rows"].extend([row, row, hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper()])
        positions["modified_cols"].extend([col, col + 1, 0])
    if col == 15:
        positions["modified_rows"].extend([row, hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(),
                                           hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper()])
        positions["modified_cols"].extend([col, 0, 1])
    return positions


class SicXE:
    def __init__(self) -> None:
        self.labelsDf = None
        self.estab = {}
        self.filepath = ""
        self.starting_address = "000000"
        self.starting_address_entry = None
        self.arr = []
        self.addresses = []
        self.lengths = []
        self.tRecs = ""
        self.unique_index = []
        self.df = None
        self.colored = {}
        self.show_menu()

    def show_menu(self):
        menu = Tk()
        menu.geometry("900x500")
        menu.title("Absolute Loader")
        labelframe = LabelFrame(menu, text="GENERATE LINKING LOADER FROM SIC-XE PROGRAM", font=("Arial", 16),
                                padx=50, pady=50)
        labelframe.pack()
        Label(labelframe, text="Enter starting address").pack()
        self.starting_address_entry = Entry(labelframe)
        self.starting_address_entry.pack()
        Button(labelframe, text="Confirm address", command=self.setEntry).pack()
        Label(labelframe, text="Import HDRTME file .txt").pack()
        button = Button(labelframe, text="Browse a file", command=self.openfile)
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
        self.starting_address = self.starting_address_entry.get()

    def generate_external_symbol_table(self):
        """
            **generate_external_symbol_table:**
        """
        hdrtme = open(self.filepath, "r")
        control_sections = []
        control_section_addresses = []
        control_section_lengths = []
        for line in hdrtme:
            if line[0] == 'H':
                name = line[1:6].replace("X", "")
                address = hex(int(line[7:13], 16) + int(self.starting_address, 16)).replace("0x", "").zfill(6).upper()
                length = line[13:].strip()
                control_sections.append(name)
                control_section_addresses.append(address)
                control_section_lengths.append(length)
            if line[0] == 'D':
                line = line.strip()
                defs = [line[i:i + 6] for i in range(1, len(line), 12)]
                defs_addresses = [line[i:i + 6] for i in range(7, len(line), 12)]
                definitions = {}
                for definition, definition_address in zip(defs, defs_addresses):
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
        self.labelsDf.to_csv("estable.txt", encoding=None, index=True, sep=' ')
        self.estab_window()

    def estab_window(self):
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
        print(self.estab)
        for line in hteRec:
            if line[0] == 'H':
                control_section_name = line[1:6]
                control_section_starting_address = self.estab[control_section_name.replace("X", "")]['address']
            if line[0] == 'T':
                x = int(line[1:7], 16) + int(control_section_starting_address, 16)
                print(hex(x))
                self.addresses.append(hex(x).replace("0x", "").zfill(6).upper())
                self.lengths.append(line[7:9])
                self.tRecs += line[9:].strip()
        self.arr = [self.tRecs[i:i + 2] for i in range(0, len(self.tRecs), 2)]
        self.arr = np.array(self.arr)

    def generate_memory(self):
        min_address = min(self.addresses)[:5] + "0"
        max_address = max(self.addresses)[:5] + "0"
        mem_addresses = np.arange(int(min_address, 16), int(max_address, 16) + 16 * 4, 16)  # 4000 -> 9000

        def format_hex_addresses(x): return hex(x).replace("0x", "").zfill(6).upper()

        mem_hex_addresses = np.array([format_hex_addresses(x) for x in mem_addresses])
        mem = np.zeros((len(mem_hex_addresses), 16), dtype=int)
        mem.astype(str)
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

    def set_colored(self, row, col):
        if col < 14:
            if self.unique_index.get_loc(row) in self.colored:
                self.colored[self.unique_index.get_loc(row)].extend([col, col + 1, col + 2])
            else:
                self.colored[self.unique_index.get_loc(row)] = [col, col + 1, col + 2]
        elif col == 14:
            if self.unique_index.get_loc(row) in self.colored:
                self.colored[self.unique_index.get_loc(row)].extend([col, col + 1])
            else:
                self.colored[self.unique_index.get_loc(row)] = [col, col + 1]
            self.colored[
                self.unique_index.get_loc(hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper())] = [0]

        elif col == 15:
            if self.unique_index.get_loc(row) in self.colored:
                self.colored[self.unique_index.get_loc(row)].extend([col])
            else:
                self.colored[self.unique_index.get_loc(row)] = [col]
            self.colored[
                self.unique_index.get_loc(hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper())] = [0, 1]

    def modify_data(self):
        hteRec = open(self.filepath, "r")
        for line in hteRec:
            firstChar = ""
            if line[0] == 'H':
                name = line[1:6].replace("X", "")
                start = self.estab[name]['address']
            if line[0] == 'M':
                z = hex(int(line[1:7], 16) + int(start, 16)).replace("0x", "").zfill(6).upper()
                row = z[0:5] + "0".upper()
                col = int(z[5:6], 16)
                length = line[7:9]
                operator = line[9:10]
                label = line[10:].strip()
                value = self.select_cell(row, col)
                self.set_colored(row, col)
                if length == '05':
                    firstChar = value[0]
                    value = value[1:]
                found_address = search_estab(estab=self.estab, label=label)
                value = modify_cell(operator=operator, first_char=firstChar, cell_val=value, length=length,
                                    found_address=found_address)
                modified_rows = return_modified_positions(row, col)['modified_rows']
                modified_cols = return_modified_positions(row, col)['modified_cols']
                self.place_new_values(modified_rows, modified_cols, value)

        print(self.df)

    def place_new_values(self, modified_rows, modified_cols, value):
        j = 0
        for r, c in zip(modified_rows, modified_cols):
            self.df.at[r, c] = value[j:j + 2]
            j += 2

    def generate_table(self):
        root = Tk()
        root.geometry("600x500")
        root.title("Linker")
        frame = Frame(root)
        frame.pack(fill="both", expand=True)
        table = Table(frame, dataframe=self.df, width=500, maxcellwidth=30)
        table.show()
        table.showindex = True
        for k, v in self.colored.items():
            print(k, v)
            table.setRowColors(rows=[k], cols=v, clr='#ADD8E6')
        root.mainloop()

    def select_cell(self, row, col):
        if col < 14:
            value = str(self.df.loc[row, col]) + str(self.df.loc[row, col + 1]) + str(
                self.df.loc[row, col + 2])
        elif col == 14:
            value = str(self.df.loc[row, col]) + str(self.df.loc[row, col + 1]) + str(
                self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 0])
        elif col == 15:
            value = str(self.df.loc[row, col]) + str(
                self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 0]) + str(
                self.df.loc[hex(int(row, 16) + 16).replace("0x", "").zfill(6).upper(), 1])
        return value ;
