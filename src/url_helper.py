from urllib.parse import urljoin, urlparse
import os.path

class UrlParser:
    """
    Класс для разбора URL на компоненты:
    схема, домен, путь, имя файла, имя без расширения и расширение.
    Игнорирует параметры запроса (?...) и фрагмент (#...).
    """
    def __init__(self, url):
        self.url = url
        self.parsed = urlparse(url)
        self.path = self.parsed.path
        self.filename = os.path.basename(self.path)
        self.name, self.extension = os.path.splitext(self.filename)

    def get_scheme(self):
        """Схема (http/https и т.д.)"""
        return self.parsed.scheme

    def get_netloc(self):
        """Домен/хост (netloc)"""
        return self.parsed.netloc

    def get_path(self):
        """Путь к файлу"""
        return self.path

    def get_filename(self):
        """Полное имя файла с расширением"""
        return self.filename

    def get_name(self):
        """Имя файла без расширения"""
        return self.name

    def get_extension(self):
        """Расширение файла (с точкой, напр. '.jpg')"""
        return self.extension

    def to_dict(self):
        """Все компоненты в словаре"""
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
    Класс для формирования полного URL из базового и относительной ссылки.
    Использует urllib.parse.urljoin для корректной обработки всех случаев:
    - относительные пути (img.jpg, ../img.jpg)
    - абсолютные пути (/img.jpg)
    - с параметрами и фрагментами.
    """
    @staticmethod
    def join(base_url, relative_url):
        """
        Формирует полный URL.

        :param base_url: Базовый URL (абсолютный)
        :param relative_url: Относительная или абсолютная ссылка на картинку
        :return: Полный абсолютный URL
        """
        return urljoin(base_url, relative_url)

    @staticmethod
    def is_absolute(url):
        """Проверяет, является ли URL абсолютным."""
        return bool(urlparse(url).scheme)

    @staticmethod
    def normalize(url):
        """Нормализует URL (убирает лишние слеши и т.д.)."""
        parsed = urlparse(url)
        return parsed._replace(path=parsed.path.rstrip('/')).geturl()
