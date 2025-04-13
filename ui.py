import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SearchApp:
    def __init__(self, root, controller, search_logger):
        self.root = root
        self.root.title("Local File Search")

        self.controller = controller
        self.search_logger = search_logger

        self.root_dir = ""
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        indexing_frame = ttk.LabelFrame(self.root, text="Indexing", padding=(10, 5))
        indexing_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Button(indexing_frame, text="Select Directory", command=self.select_directory).grid(row=0, column=0)
        self.dir_label = ttk.Label(indexing_frame, text="No directory selected")
        self.dir_label.grid(row=0, column=1)
        ttk.Button(indexing_frame, text="Start Indexing", command=self.start_indexing).grid(row=0, column=2)

        search_frame = ttk.LabelFrame(self.root, text="Search", padding=(10, 5))
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(search_frame, text="Search Query:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1)

        self.suggestions_listbox = tk.Listbox(search_frame, height=3)
        self.suggestions_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.load_suggestion)

        results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=(10, 5))
        results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.results_listbox = tk.Listbox(results_frame, height=10, width=50)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.results_listbox.bind("<<ListboxSelect>>", self.show_preview)

        self.preview_label = ttk.Label(results_frame, text="", wraplength=400, foreground="gray")
        self.preview_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.search_var.trace_add("write", self.on_search_change)

    def select_directory(self):
        self.root_dir = filedialog.askdirectory()
        if self.root_dir:
            self.dir_label.config(text=self.root_dir)

    def start_indexing(self):
        if self.root_dir:
            self.controller.index_directory(self.root_dir)
            messagebox.showinfo("Indexing", "Indexing complete!")
        else:
            messagebox.showwarning("Indexing", "Please select a directory first.")

    def on_search_change(self, *args):
        query = self.search_var.get().strip()

        # Suggestions
        self.suggestions_listbox.delete(0, tk.END)
        if query:
            suggestions = self.search_logger.get_suggestions(query)
            for s in suggestions:
                self.suggestions_listbox.insert(tk.END, s)

        # Search and ranking
        if query:
            results = self.controller.search(query)
            print("Raw search results:", results)

            ranked = self.search_logger.rank_results(query, results)
            self.update_results(ranked)
            print("Ranked search results:", results)

            # Notify observer
            self.search_logger.update(query)

    def load_suggestion(self, event):
        selection = self.suggestions_listbox.curselection()
        if selection:
            suggestion = self.suggestions_listbox.get(selection[0])
            self.search_var.set(suggestion)

    def update_results(self, results):
        self.results_listbox.delete(0, tk.END)
        for path, score in results:
            self.results_listbox.insert(tk.END, f"{path} (Score: {score})")

    def show_preview(self, event):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            file_entry = self.results_listbox.get(selected_index)
            file_path = file_entry.split(" (Score:")[0]  # Strip off score part
            preview = self.controller.get_preview(file_path)
            self.preview_label.config(text=f"Preview: {preview}")

    def on_close(self):
        self.controller.cleanup()
        self.root.destroy()
