import asyncio
import json
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from base64 import b64decode
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlResult, CrawlerRunConfig

class CrawlArchiveWriter:
    def write_meta(self, zip_file: ZipFile, crawl_result: CrawlResult):
        """
        Metadata metadata.json
        """
        meta = {
            "url": crawl_result.url,
            "content_length": len(crawl_result.html or ""),
            "response_headers": getattr(crawl_result, "response_headers", []) or []
        }
        zip_file.writestr("metadata.json", json.dumps(meta, indent=2, ensure_ascii=False))

    def write_pdf(self, zip_file: ZipFile, crawl_result: CrawlResult):
        if crawl_result.pdf:
            zip_file.writestr("page.pdf", crawl_result.pdf)

    def write_screenshot(self, zip_file: ZipFile, crawl_result: CrawlResult):
        """
        Screenshot
        """
        if crawl_result.screenshot:
            zip_file.writestr("screenshot.png", b64decode(crawl_result.screenshot))

    def write_html(self, zip_file: ZipFile, crawl_result: CrawlResult):
        """
        Raw HTML
        """
        zip_file.writestr("index.html", crawl_result.html or "")

    def write_mhtml(self, zip_file: ZipFile, crawl_result: CrawlResult):
        """
        MHTML
        """
        if crawl_result.mhtml:
            zip_file.writestr("index.mhtml", crawl_result.mhtml or "")

class CrawlArchiverConfig:
    def __init__(self,
                 browser_config: BrowserConfig,
                 run_config: CrawlerRunConfig):
        self.browser_config = browser_config
        self.run_config = run_config

class CrawlArchiverResult:
    def __init__(self,
                 url: str,
                 zip_buffer: bytes):
        self.url = url
        self.zip_buffer = zip_buffer

class CrawlArchiver:
    def __init__(self,
                 config: CrawlArchiverConfig,
                 writer: CrawlArchiveWriter):
        self.config = config
        self.writer = writer

    async def download(self, url: str) -> CrawlArchiverResult:
        """Processes a single URL and returns a ZIP buffer."""
        async with AsyncWebCrawler(config=self.config.browser_config) as crawler:
            result: CrawlResult = await crawler.arun(url=url, config=self.config.run_config) # type: ignore

        # Yield control to complete all async crawler operations
        await asyncio.sleep(0.1)

        # We write the result into a zip archive.
        return self.__zip_result_to_buffer(result)

    def __zip_result_to_buffer(self, crawl_result: CrawlResult) -> CrawlArchiverResult:
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
            # Pdf
            self.writer.write_pdf(zf, crawl_result)
            # Screenshot
            self.writer.write_screenshot(zf, crawl_result)
            # Raw HTML
            self.writer.write_html(zf, crawl_result)
            # MHTML
            self.writer.write_mhtml(zf, crawl_result)
            # Meta JSON
            self.writer.write_meta(zf, crawl_result)

        zip_bytes = buffer.getvalue()
        return CrawlArchiverResult(crawl_result.url, zip_bytes)


