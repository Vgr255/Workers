from tkinter import *
from tkinter import filedialog

import sys

__version__ = "0.3"

FONT_TABLE = {0x00: "A", 0x01: "B", 0x02: "C", 0x03: "D",
              0x04: "E", 0x05: "F", 0x06: "G", 0x07: "H",
              0x08: "I", 0x09: "J", 0x0A: "K", 0x0B: "L",
              0x0C: "M", 0x0D: "N", 0x0E: "O", 0x0F: "P",
              0x10: "Q", 0x11: "R", 0x12: "S", 0x13: "T",
              0x14: "U", 0x15: "V", 0x16: "W", 0x17: "X",
              0x18: "Y", 0x19: "Z", 0x1A: "1", 0x1B: "2",
              0x1C: ":", 0x1D: ",", 0x1E: ".", 0x1F: "&",
              0x20: "(", 0x21: ")", 0x22: "'", 0x23: "“",
              0x24: "”", 0x25: "-", 0x26: "3", 0x27: "Å",
              0x2F: " ", 0x30: "\n"}

reverse_font_table = str.maketrans({v:chr(k) for k,v in FONT_TABLE.items()})

"""
0x28=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x29=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x2A=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x2B=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x2C=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x2D=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
0x2E=(SPECIAL ACCENTED CHARACTER, CHANGES WITH EACH LANGUAGE)
"""

class Open(filedialog.Open):
    "Fixed version of commondialog.Dialog based on filedialog.Open"

    def show(self, **options):

        # update instance options
        for k, v in options.items():
            self.options[k] = v

        self._fixoptions()

        # we need a dummy widget to properly process the options
        # (at least as long as we use Tkinter 1.63)
        w = Frame(Tk())
        w.pack()
        w.master.withdraw()

        try:

            s = w.tk.call(self.command, *w._options(self.options))
            s = self._fixresult(w, s)

        finally:

            # get rid of the widget
            w.master.destroy()

        return s

class MainWindow(Frame):
    def __init__(self, file=None):
        super().__init__(Tk())
        self.pack()
        self.master.title("Workers v%s" % __version__)

        # The actual list of items where all of our lines are

        self.textscroll = Scrollbar(self, orient=VERTICAL)
        self.textlist = Listbox(self, yscrollcommand=self.textscroll.set)
        self.textscroll["command"] = self.textlist.yview
        self.textscroll.pack(side=RIGHT, fill=Y)
        self.textlist.pack(side=RIGHT, fill=Y, expand=YES)

        # Menu bar and dropdown menus

        self.menubar = Menu(self)

        self.filemenu = Menu(self.menubar, tearoff=NO)
        self.filemenu.add_command(label="Open", command=lambda: self.run_program(self.load_file()))
        self.filemenu.add_command(label="Reload from disk", command=self.reload_from_disk)
        self.filemenu.add_command(label="Save", command=self.write_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.master.destroy)

        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = Menu(self.menubar, tearoff=NO)
        self.helpmenu.add_command(label="About", command=self.about_menu)

        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.master["menu"] = self.menubar

        # Edit fields where everything can be set

        self.font_type_label = Label(self, text="Font Type")
        self.font_type_label.pack(side=LEFT, anchor=NW)

        self.font_type_entry = StringVar()
        self.font_type = Entry(self, textvariable=self.font_type_entry, state=DISABLED)
        self.font_type.pack(side=TOP, anchor=N)

        self.font_color_label = Label(self, text="Font Color")
        self.font_color_label.pack(side=LEFT, anchor=NW)

        self.font_color_entry = StringVar()
        self.font_color = Entry(self, textvariable=self.font_color_entry, state=DISABLED)
        self.font_color.pack(side=TOP, anchor=N)

        self.line_contents_label = Label(self, text="Line Contents")
        self.line_contents_label.pack(side=LEFT, anchor=NW)

        self.line_contents = Text(self, state=DISABLED)
        self.line_contents.pack(side=TOP, anchor=N)

        # Setup the internals

        self.lines = []
        self.current = None

        # Initialization complete, now let's load the file

        self.file = file

        if file is None:
            file = self.load_file()
            if file is None:
                return # cancelled out

        self.run_program(file)

    def reload_from_disk(self):
        self.current = None
        self.lines[:] = []
        self.textlist.delete(0, END)
        self.font_type_entry.set("")
        self.font_color_entry.set("")
        self.line_contents.delete(1.0, END)
        self.run_program(self.file)

    def run_program(self, file):
        if not file:
            return
        self.font_type["state"] = NORMAL
        self.font_color["state"] = NORMAL
        self.line_contents["state"] = NORMAL

        with open(file, "rb") as f:
            content = f.read()
            count = len(content) / 64
            if not count.is_integer():
                self.error_message("File does not have a multiple of 64 bytes")
                return

            for n in range(int(count)):
                self.textlist.insert(END, "Entry #%s" % n)
                self.lines.append([content[:0x04], content[0x04:0x08], content[0x08:0x0C], content[0x0C:0x3C], content[0x3C:0x40]])
                content = content[0x40:]

        self.check_update()

    def check_update(self):
        cur = self.textlist.curselection()
        if cur and cur[0] != self.current:
            self.save_selection()
            self.current = int(cur[0])
            self.update_selection()
        self.after(250, self.check_update)

    def update_selection(self):
        self.font_type_entry.set(int.from_bytes(self.lines[self.current][0], "little"))
        self.font_color_entry.set(int.from_bytes(self.lines[self.current][1], "little"))
        self.line_contents.delete(1.0, END)
        line = self.lines[self.current][3].decode("ascii").translate(FONT_TABLE)
        self.line_contents.insert(END, line[:line.index("\x7f")])

    def save_selection(self):
        if self.current is not None:
            line = self.line_contents.get(1.0, END)
            if len(line) >= 48:
                self.error_message("Text length must be < 48 characters\nEntry not saved")
                return

            line = line.upper()
            s = set(line) - set(FONT_TABLE.values())

            if s:
                self.error_message("Characters not supported:\n{0}\nEntry not saved".format(", ".join(s)))
                return

            self.lines[self.current][0] = int(self.font_type_entry.get()).to_bytes(4, "little")
            self.lines[self.current][1] = int(self.font_color_entry.get()).to_bytes(4, "little")

            line = list(line.translate(reverse_font_table).encode("ascii"))
            line.append(127)
            while len(line) < 48:
                line.append(0)

            self.lines[self.current][3] = bytes(line)

    def write_file(self):
        self.save_selection()
        filetypes = [("PEOPLE.BIN", ".bin"), ("All files", "*")]
        file = filedialog.SaveAs(filetypes=filetypes).show()
        if file:
            with open(file, "wb") as f:
                for data in self.lines:
                    f.write(b"".join(data))

    def load_file(self):
        filetypes = [("PEOPLE.BIN", ".bin"), ("All files", "*")]
        file = Open(filetypes=filetypes).show()
        if file:
            self.file = file
            return file
        self.master.destroy()

    def error_message(self, msg):
        window = Frame(Tk())
        window.pack()
        window.master.title("Error")

        label = Label(window, text=msg)
        label.pack(side=TOP)

        ok = Button(window, text="OK", command=window.master.destroy)
        ok.pack(side=BOTTOM)

    def about_menu(self):
        window = Frame(Tk())
        window.pack()
        window.master.title("About Workers %s" % __version__)

        label = Label(window, text="Workers {0} created by Vgr\nFormat research by IlDucci".format(__version__))
        label.pack(side=TOP)

        ok = Button(window, text="OK", command=window.master.destroy)
        ok.pack(side=BOTTOM)

if __name__ == "__main__":
    MainWindow(len(sys.argv) > 1 and sys.argv[1] or None).mainloop()
