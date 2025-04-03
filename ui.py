import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import database
import indexer

class SearchApp:
    def __init__(self, uiRoot):
        self.preview_label = None
        self.dir_label = None
        self.search_entry = None
        self.results_listbox = None
        self.root = uiRoot
        self.root.title("Local File Search")

        # Database connection details (replace with your actual values)
        self.db_name = "filesystem"
        self.db_user = "postgres"
        self.db_password = "parola789"
        self.db_host = "localhost"
        self.db_port = "5432"

        self.create_widgets()
        self.root_dir = ""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # 1. Indexing Section
        indexing_frame = ttk.LabelFrame(self.root, text="Indexing", padding=(10, 5))
        indexing_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Button(indexing_frame, text="Select Directory", command=self.select_directory).grid(row=0, column=0, padx=5,
                                                                                                pady=2)
        self.dir_label = ttk.Label(indexing_frame, text="No directory selected")
        self.dir_label.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(indexing_frame, text="Start Indexing", command=self.start_indexing).grid(row=0, column=2, padx=5,
                                                                                            pady=2)

        # 2. Search Section
        search_frame = ttk.LabelFrame(self.root, text="Search", padding=(10, 5))
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(search_frame, text="Search Query:").grid(row=0, column=0, padx=5, pady=2)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=2)

        # 3. Results Section
        results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=(10, 5))
        results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.results_listbox = tk.Listbox(results_frame, height=10, width=50)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        # Bind the listbox selection event to show preview
        self.results_listbox.bind("<<ListboxSelect>>", self.show_preview)

        # Preview label (appears below the listbox)
        self.preview_label = ttk.Label(results_frame, text="", wraplength=400, foreground="gray")
        self.preview_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")  # Positioned under listbox

        # Bind the entry's text change event to perform_search
        self.search_var.trace_add("write", self.on_search_change)

    def select_directory(self):
        self.root_dir = filedialog.askdirectory()
        if self.root_dir:
            self.dir_label.config(text=self.root_dir)
#controller!!
    def start_indexing(self):
        if self.root_dir:
            indexer.crawl_and_index(self.root_dir, self.db_name, self.db_user, self.db_password, self.db_host, self.db_port)
            tk.messagebox.showinfo("Indexing", "Indexing complete!")
        else:
            tk.messagebox.showwarning("Indexing", "Please select a directory first.")

    def perform_search(self, query):
        if query:
            results = database.search_files(self.db_name, self.db_user, self.db_password, self.db_host, self.db_port,
                                            query)
            self.update_results(results)
        else:
            self.update_results([])  # Clear results if the query is empty

    def update_results(self, results):
        self.results_listbox.delete(0, tk.END)  # Clear previous results
        self.results_listbox.results_date=results
        for path, preview  in results:
            display_text=f"{path}"
            self.results_listbox.insert(tk.END, display_text)

    def on_search_change(self, *args):
        """
        This function is called whenever the text in the search entry changes.
        """
        query = self.search_var.get()
        self.perform_search(query)

    def on_close(self):
        """Clears the database and closes the application."""
        database.clear_database(self.db_name, self.db_user, self.db_password, self.db_host, self.db_port)
        self.root.destroy()  # Close the UI

    def show_preview(self, event):
        """Displays a short preview of the selected file."""
        selected_index = self.results_listbox.curselection()
        if selected_index:
            file_path = self.results_listbox.get(selected_index)
            if database.is_txt(self.db_name, self.db_user, self.db_password, self.db_host, self.db_port, file_path):
                preview_text = database.get_file_preview(self.db_name, self.db_user, self.db_password, self.db_host,
                                                     self.db_port, file_path)
            else:
                preview_text = ""
            # Display the first few words in the preview label
            self.preview_label.config(text=f"Preview: {preview_text}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)
    root.mainloop()
