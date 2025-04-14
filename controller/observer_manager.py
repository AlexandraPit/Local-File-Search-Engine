class ObserverManager:
    def __init__(self):
        self.observers = []

    def register(self, observer):
        self.observers.append(observer)

    def get_frequent_terms(self):
        for obs in self.observers:
            if hasattr(obs, "get_frequent_terms"):
                return obs.get_frequent_terms()
        return []
