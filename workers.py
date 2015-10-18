from tkinter import *
from tkinter import filedialog

import sys

__version__ = "0.1"

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
        self.textlist.pack(side=RIGHT, fill=Y, expand=True)

        # Adding this for completion's sake

        self.quit_button = Button(self, text="Quit", command=self.master.destroy)
        self.quit_button.pack(side=BOTTOM)

        # Menu bar and dropdown menus

        self.menubar = Menu(self)

        self.filemenu = Menu(self.menubar, tearoff=False)
        self.filemenu.add_command(label="Open", command=lambda: self.run_program(self.load_file()))
        self.filemenu.add_command(label="Reload from disk", command=lambda: self.run_program(open(self.file, "rb")))
        self.filemenu.add_command(label="Save", command=self.write_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.master.destroy)

        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = Menu(self.menubar, tearoff=False)
        self.helpmenu.add_command(label="About", command=self.about_menu)

        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        self.master["menu"] = self.menubar

        # Edit fields where everything can be set

        self.font_type_entry = StringVar()
        self.font_type = Entry(self, textvariable=self.font_type_entry, state=DISABLED)
        self.font_type.pack()

        # Setup the internals

        self.lines = []

        # Initialization complete, now let's load the file

        self.file = file

        if file is None:
            file = self.load_file()
            if file is None:
                return # cancelled out

        self.run_program(file)

    def run_program(self, file):
        if not file:
            return
        self.font_type["state"] = NORMAL
        

    def write_file(self):
        pass

    def load_file(self):
        filetypes = [("PEOPLE.BIN", ".bin"), ("All files", "*")]
        file = Open(filetypes=filetypes).show()
        if file:
            self.file = file
            return open(file, "rb")
        self.master.destroy()

    def about_menu(self):
        pass

if __name__ == "__main__":
    MainWindow(len(sys.argv) > 1 and sys.argv[1] or None).mainloop()
