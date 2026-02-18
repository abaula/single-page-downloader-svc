from enum import IntEnum
from dynaconf import Dynaconf

class LoaderType(IntEnum):
    DYNAMIC = 0  # Loading dynamic content
    STATIC = 1   # Loading static content

class Request:
    def __init__(self,
                 url: str,
                 loader_type: LoaderType):
        self.url = url
        self.loader_type = loader_type

class Response:
    def __init__(self,
                 original_url: str,
                 zip_archive: bytes):
        self.original_url = original_url
        self.zip_archive = zip_archive

class PageDownloader:
    def __init__(self,
                 settings: Dynaconf):
        self.settings = settings

    def download(self, request: Request) -> Response:
        pass