import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from classes import CompressJob

class BulkConverterGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.jobs = []
        self.path_var = tk.StringVar()
        self.dst_var = tk.StringVar()
        self.rule_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        #self.confirm_var = tk.BooleanVar()
        self.auto_cbz_var = tk.BooleanVar(value=True)
        self.ignore_missmatching_var = tk.BooleanVar(value=False)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)
        tk.Label(self, text="Source:").grid(row=0, column=0, padx=10, pady=5)
        self.path_entry = tk.Entry(self, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Button(self, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self, text="Destination:").grid(row=1, column=0, padx=10, pady=5)
        self.dst_entry = tk.Entry(self, textvariable=self.dst_var)
        self.dst_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Button(self, text="Browse", command=self.browse_destination).grid(row=1, column=2, padx=10, pady=5)

        tk.Label(self, text="Regex:").grid(row=2, column=0, padx=10, pady=5)
        self.rule_entry = tk.Entry(self, textvariable=self.rule_var)
        self.rule_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.regex_options = tk.Frame(self)
        self.regex_options.grid(row=2, column=2, padx=10, pady=5)
        tk.Checkbutton(self.regex_options, variable=self.ignore_missmatching_var).pack(side=tk.LEFT)
        tk.Label(self.regex_options, text="Match only").pack(side=tk.LEFT)

        tk.Label(self, text="Replace:").grid(row=3, column=0, padx=10, pady=5)
        self.replace_entry = tk.Entry(self, textvariable=self.replace_var)
        self.replace_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        self.replace_options = tk.Frame(self)
        self.replace_options.grid(row=3, column=2, padx=10, pady=5)
        tk.Checkbutton(self.replace_options, variable=self.auto_cbz_var).pack(side=tk.LEFT)
        tk.Label(self.replace_options, text=".cbz").pack(side=tk.LEFT)

        columns = ("src", "dst")
        self.tree = ttk.Treeview(self, columns=columns)
        self.tree['show'] = 'headings'
        self.tree.heading("src", text="Source")
        self.tree.column("src", minwidth=0, width=100)
        self.tree.heading("dst", text="Destination")
        self.tree.column("dst", minwidth=0, width=100)
        self.tree.grid(row=4, column=0, columnspan=3, padx=(10, 23), pady=(10, 5), sticky="nsew")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=4, column=2, columnspan=3, padx=10, pady=(10, 5), sticky="nse")

        self.action_frame = tk.Frame(self)
        self.action_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.load_button = ttk.Button(self.action_frame, text="Load", command=self.load_jobs)
        self.load_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.convert_button = ttk.Button(self.action_frame, text="Convert", command=self.convert_jobs)
        self.convert_button.pack(side=tk.RIGHT, padx=10, pady=5)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            self.clear_jobs()
            self.clear_tree()
    
    def browse_destination(self):
        path = filedialog.askdirectory()
        if path:
            self.dst_var.set(path)

    def load_jobs(self):
        path = self.path_var.get()
        if not os.path.exists(path):
            messagebox.showwarning("Warning", f"Path \"{path}\" does not exist.")
            return
        
        src = self.path_var.get()
        dst = self.dst_var.get()
        if dst == "":
            dst = src

        rule = self.rule_var.get()
        if rule == "":
            rule = None

        replace = self.replace_var.get()
        if replace == "":
            replace = None
        elif self.auto_cbz_var.get():
            replace = replace + ".cbz"

        self.jobs = CompressJob.get_jobs(src, dst, rule, replace, ignore_not_matching=self.ignore_missmatching_var.get())
        self.clear_tree()
        self.populate_tree()

    def clear_jobs(self):
        self.jobs = []
        self.clear_tree()

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)


    def populate_tree(self):
        for job in self.jobs:
            self.tree.insert('', 'end', values=[job.src_name, job.dst_name])

    def convert_jobs(self):
        try:
            for job in self.jobs:
                job.compress()
        except Exception as e:
            messagebox.showerror("Error", str(e))

        messagebox.showinfo("Done", "Operation completed.")


if __name__ == "__main__":
    import argparse
    import logging
    import sys

    parser = argparse.ArgumentParser(description="Makes a cbz file out of every folder at a given path")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if args.verbose else logging.INFO)

    window = tk.Tk()
    window.title("Bulk Converter GUi")
    window.geometry("480x640")
    app = BulkConverterGUI(master=window)
    app.pack(fill="both", expand=True)
    window.mainloop()