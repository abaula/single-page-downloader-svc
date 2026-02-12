from urllib.parse import urljoin, urlparse
import os.path

class UrlParser:
    """
    A class for parsing URLs into their components:
    scheme, domain, path, filename, name without extension, and extension.
    Ignores query parameters (?...) and fragments (#...).
    """
    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
        self.path = self.parsed.path
        self.filename = os.path.basename(self.path)
        self.name, self.extension = os.path.splitext(self.filename)

    def get_scheme(self):
        """Scheme (http/https, etc.)"""
        return self.parsed.scheme

    def get_netloc(self):
        """Domain/host (netloc)"""
        return self.parsed.netloc

    def get_path(self):
        """File path"""
        return self.path

    def get_filename(self):
        """Full file name with extension"""
        return self.filename

    def get_name(self):
        """File name without extension"""
        return self.name

    def get_extension(self):
        """File extension (with a period, e.g. 'jpg')"""
        return self.extension

    def to_dict(self):
        """All components in the dictionary"""
        return {
            'scheme': self.get_scheme(),
            'netloc': self.get_netloc(),
            'path': self.get_path(),
            'filename': self.get_filename(),
            'name': self.get_name(),
            'extension': self.get_extension()
        }

class UrlJoiner:
    """
    A class for forming a full URL from a base and a relative link.
    Uses urllib.parse.urljoin to correctly handle all cases:
    - relative paths (img.jpg, ../img.jpg)
    - absolute paths (/img.jpg)
    - with parameters and fragments.
    """
    @staticmethod
    def join(base_url, relative_url):
        """
        Generates a full URL.
        :param base_url: Base URL (absolute)
        :param relative_url: Relative or absolute link to the image
        :return: Full absolute URL
        """
        return urljoin(base_url, relative_url)

    @staticmethod
    def is_absolute(url):
        """Checks if the URL is absolute."""
        return bool(urlparse(url).scheme)

    @staticmethod
    def normalize(url):
        """Normalizes URLs (removes extra slashes, etc.)."""
        parsed = urlparse(url)
        return parsed._replace(path=parsed.path.rstrip('/')).geturl()
