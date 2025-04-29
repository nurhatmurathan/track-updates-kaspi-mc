class HttpRequestError(Exception):
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        self.message = message[:300]

    def __str__(self):
        return repr(f"Error request {self.url} status code: {self.status_code}: {self.message}")
