import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Constants for UI sizes
LISTBOX_HEIGHT = 10
LISTBOX_WIDTH = 50

class SearchApp:
    def __init__(self, root, controller, search_logger):
        self.root = root
        self.root.title("Local File Search")

        self.controller = controller
        self.search_logger = search_logger

        self.root_dir = ""
        self.path_score_map = {}  # To map paths to their scores
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.create_indexing_section()
        self.create_search_section()
        self.create_results_section()
        self.search_var.trace_add("write", self.on_search_change)

    def create_indexing_section(self):
        indexing_frame = ttk.LabelFrame(self.root, text="Indexing", padding=(10, 5))
        indexing_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Button(indexing_frame, text="Select Directory", command=self.select_directory).grid(row=0, column=0)
        self.dir_label = ttk.Label(indexing_frame, text="No directory selected")
        self.dir_label.grid(row=0, column=1)
        ttk.Button(indexing_frame, text="Start Indexing", command=self.start_indexing).grid(row=0, column=2)

    def create_search_section(self):
        search_frame = ttk.LabelFrame(self.root, text="Search", padding=(10, 5))
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(search_frame, text="Search Query:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1)

        self.suggestions_listbox = tk.Listbox(search_frame, height=3)
        self.suggestions_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.load_suggestion)

    def create_results_section(self):
        results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=(10, 5))
        results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.results_listbox = tk.Listbox(results_frame, height=LISTBOX_HEIGHT, width=LISTBOX_WIDTH)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.results_listbox.bind("<<ListboxSelect>>", self.show_preview)

        self.preview_label = ttk.Label(results_frame, text="", wraplength=400, foreground="gray")
        self.preview_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    def select_directory(self):
        self.root_dir = filedialog.askdirectory()
        if self.root_dir:
            self.dir_label.config(text=self.root_dir)

    def start_indexing(self):
        if self.root_dir:
            try:
                self.controller.index_directory(self.root_dir)
                messagebox.showinfo("Indexing", "Indexing complete!")
            except Exception as e:
                messagebox.showerror("Error", f"Indexing failed: {e}")
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
            try:
                results = self.controller.search(query)
                print("Raw search results:", results)

                # Rank the results
                ranked = self.search_logger.rank_results(query, results)
                self.update_results(ranked)
                print("Ranked search results:", ranked)

                # Notify observer
                self.search_logger.update(query)
            except Exception as e:
                messagebox.showerror("Search Error", f"An error occurred while searching: {e}")

    def load_suggestion(self, event):
        selection = self.suggestions_listbox.curselection()
        if selection:
            suggestion = self.suggestions_listbox.get(selection[0])
            self.search_var.set(suggestion)

    def update_results(self, results):
        self.results_listbox.delete(0, tk.END)
        self.path_score_map = {}  # Reset mapping
        for path, score in results:
            self.results_listbox.insert(tk.END, f"{path} (Score: {score})")
            self.path_score_map[path] = (score)  # Store path-to-score mapping

    def show_preview(self, event):
        selected_index = self.results_listbox.curselection()
        if selected_index:
            file_entry = self.results_listbox.get(selected_index)
            file_path = file_entry.rsplit(" (Score:", 1)[0]  # Safer parsing of file path
            preview = self.controller.get_preview(file_path)
            self.preview_label.config(text=f"Preview: {preview}")

    def on_close(self):
        self.controller.cleanup()
        self.root.destroy()
