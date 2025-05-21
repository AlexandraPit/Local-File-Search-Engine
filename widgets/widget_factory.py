import tkinter as tk

class WidgetFactory:
    def __init__(self):
        self.rules = [
            (self.is_log_files, self.create_log_widget),
            (self.is_image_files, self.create_gallery_widget),
            (self.is_calculator, self.create_calculator_widget),
            (self.is_clock, self.create_clock_widget),
        ]

    def get_widgets(self, results, query=None):
        return [creator() for condition, creator in self.rules if condition(results, query)]

    def is_log_files(self, results, query=None):
        return any(path.endswith(".log") for path, _ in results)

    def is_image_files(self, results, query=None):
        return sum(1 for path, _ in results if path.endswith(('.jpg', '.png', '.jpeg'))) >= 3

    def is_calculator(self, results, query):
        return query and "calculator" in query.lower()

    def is_clock(self, results, query):
        return query and "clock" in query.lower()

    def create_log_widget(self):
        return lambda frame: tk.Label(frame, text="Analyze Logs Widget").pack()

    def create_gallery_widget(self):
        return lambda frame: tk.Label(frame, text="View as Gallery Widget").pack()

    def create_calculator_widget(self):
        return lambda frame: tk.Label(frame, text="Calculator Widget (Mockup)", font=("Arial", 12)).pack()

    def create_clock_widget(self):
        from time import strftime
        return lambda frame: tk.Label(frame, text=f"Current time: {strftime('%H:%M:%S')}", font=("Arial", 12)).pack()