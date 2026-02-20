from enum import IntEnum
from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig
from dynaconf import Dynaconf
from crawler import CrawlArchiveWriter, CrawlArchiver, CrawlArchiverConfig
from static_downloader import StaticContentArchiver

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
        self.crawl_archiver = None
        self.static_archiver = None

    async def download(self, request: Request) -> Response:
        request.loader_type
        match request.loader_type:
            case LoaderType.DYNAMIC:
                return await self.__download_dynamic(request.url)
            case LoaderType.STATIC:
                return await self.__download_static(request.url)
            case _:
                raise Exception(f"Unsupported loader type: {request.loader_type.name}")

    async def __download_static(self, url: str) -> Response:
        result = await self.__get_static_archiver().download(url)
        return Response(result.url, result.zip_buffer)

    async def __download_dynamic(self, url: str) -> Response:
        result = await self.__get_crawl_archiver().download(url)
        return Response(result.url, result.zip_buffer)

    def __get_static_archiver(self) -> StaticContentArchiver:
        if not self.static_archiver:
            self.static_archiver = StaticContentArchiver()
        return self.static_archiver

    def __get_crawl_archiver(self) -> CrawlArchiver:
        if not self.crawl_archiver:
            self.crawl_archiver = self.__create_crawl_archiver()
        return self.crawl_archiver

    def __create_crawl_archiver(self) -> CrawlArchiver:
        zip_content_writer = CrawlArchiveWriter()

        browser_config = BrowserConfig(
            headless=self.settings.browser.headless,
            verbose=self.settings.browser.verbose,
            # настройки против утечек ресурсов в headless browser
            use_persistent_context=False,
            browser_mode="docker",
            sleep_on_close=True,
            viewport={"width": 1280, "height": 720},  # Фиксированный viewport
            extra_args=["--disable-extensions", "--no-sandbox"]  # Доп. флаги Chrome
            )

        run_config = CrawlerRunConfig(
            capture_mhtml=self.settings.crawler.capture_mhtml,
            screenshot=self.settings.crawler.screenshot,
            pdf=self.settings.crawler.pdf,
            cache_mode=CacheMode[self.settings.crawler.cache_mode],
            verbose=self.settings.crawler.verbose,
            wait_for_images=self.settings.crawler.wait_for_images)

        config = CrawlArchiverConfig(
            browser_config=browser_config,
            run_config=run_config)

        archiver = CrawlArchiver(
            config=config,
            writer=zip_content_writer)

        return archiver