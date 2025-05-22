import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from indexer.metadata_analyzer import ResultMetadataAnalyzer
from spelling_corrector.facade import SpellingCorrectionFacade
from widgets.widget_factory import WidgetFactory

# Constants for UI sizes
LISTBOX_HEIGHT = 10
LISTBOX_WIDTH = 50



class SearchApp:
    def __init__(self, root, controller, search_logger):
        self.widget_factory = WidgetFactory()
        self.query_corrector = SpellingCorrectionFacade()

        self.root = root
        self.root.title("Local File Search")
        self.root.geometry("700x600")

        self.controller = controller
        self.search_logger = search_logger

        self.root_dir = ""
        self.path_score_map = {}

        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.widget_frame = tk.Frame(self.root, bg="lightgray", width=300)
        self.widget_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=3)  # Left side grows more
        self.root.grid_columnconfigure(1, weight=1)

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        self.create_indexing_section()
        self.create_search_section()
        self.create_results_section()
        self.search_var.trace_add("write", self.on_search_change)

    def create_indexing_section(self):
        indexing_frame = ttk.LabelFrame(self.left_frame, text="Indexing", padding=(10, 5))
        indexing_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Button(indexing_frame, text="Select Directory", command=self.select_directory).grid(row=0, column=0)
        self.dir_label = ttk.Label(indexing_frame, text="No directory selected")
        self.dir_label.grid(row=0, column=1)
        ttk.Button(indexing_frame, text="Start Indexing", command=self.start_indexing).grid(row=0, column=2)

    def create_search_section(self):
        search_frame = ttk.LabelFrame(self.left_frame, text="Search", padding=(10, 5))
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(search_frame, text="Search Query:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1)

        self.suggestions_listbox = tk.Listbox(search_frame, height=3)
        self.suggestions_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.suggestions_listbox.bind("<<ListboxSelect>>", self.load_suggestion)

    def create_results_section(self):
        results_frame = ttk.LabelFrame(self.left_frame, text="Search Results", padding=(10, 5))
        results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.results_listbox = tk.Listbox(results_frame, height=LISTBOX_HEIGHT, width=LISTBOX_WIDTH)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        self.results_listbox.bind("<<ListboxSelect>>", self.show_preview)

        self.preview_label = ttk.Label(results_frame, text="", wraplength=400, foreground="gray")
        self.preview_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

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
        corrected_query = self.query_corrector.correct(query)
        if corrected_query != query:
            print(f"Did you mean: {corrected_query}?")

        # Suggestions
        self.suggestions_listbox.delete(0, tk.END)
        if corrected_query:
            suggestions = self.search_logger.get_suggestions(corrected_query)
            for s in suggestions:
                self.suggestions_listbox.insert(tk.END, s)

        # Search and ranking
        if corrected_query:
            try:
                results = self.controller.search(corrected_query)
                self.update_results(results)
                self.show_context_widgets(results, corrected_query)
                print("Ranked search results:", results)

                analyzer = ResultMetadataAnalyzer(results)
                file_type_counts = analyzer.summarize_file_types()
                year_counts = analyzer.summarize_modified_years()
                language_counts = analyzer.summarize_languages()
                self.show_metadata_summary(file_type_counts, year_counts, language_counts)
                # Notify observer
                self.search_logger.update(corrected_query)
            except Exception as e:
                messagebox.showerror("Search Error", f"An error occurred while searching: {e}")


    def load_suggestion(self, event):
        selection = self.suggestions_listbox.curselection()
        if selection:
            suggestion = self.suggestions_listbox.get(selection[0])
            self.search_var.set(suggestion) #nume mai bun

    def update_results(self, results):
        self.results_listbox.delete(0, tk.END)
        self.path_score_map = {}
        for item in results:
            path = item["path"]
            score = item["score"]
            self.results_listbox.insert(tk.END, f"{path} (Score: {score})")
            self.path_score_map[path] = score

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

    def show_context_widgets(self, results, query):
        for child in self.widget_frame.winfo_children():
            child.destroy()

        widget_creators = self.widget_factory.get_widgets(results, query)

        for create_widget in widget_creators:
            create_widget(self.widget_frame)

    def show_metadata_summary(self, file_type_counts, year_counts, language_counts):
        tk.Label(self.widget_frame, text="Metadata Summary", font=("Arial", 14, "bold")).pack()

        def add_section(title, counter):
            tk.Label(self.widget_frame, text=title, font=("Arial", 12, "underline")).pack()
            for k, v in counter.items():
                tk.Label(self.widget_frame, text=f"{str(k).upper()} ({v})").pack()

        add_section("File Types", file_type_counts)
        add_section("Modified Years", year_counts)
        add_section("Languages", language_counts)

