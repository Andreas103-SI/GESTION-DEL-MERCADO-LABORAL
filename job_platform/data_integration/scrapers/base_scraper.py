class BaseScraper:
    def __init__(self, source_name, base_url):
        self.source_name = source_name
        self.base_url = base_url

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement run method")