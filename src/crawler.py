import asyncio
import json
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from base64 import b64decode
from typing import Dict, List
import aiohttp
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlResult, CrawlerRunConfig
from url_helper import UrlParser, UrlJoiner

class CrawlArchiveWriter:
    def write_meta(self, zip_file: ZipFile, crawl_result: CrawlResult):
        """
        Метаданные metadata.json
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

    def write_local_html(self, zip_file: ZipFile, crawl_result: CrawlResult, media_images: Dict[str, bytes]):
        """
        Local HTML
        """
        if (not crawl_result.html
            or not media_images):
            return

        # Заменяем src в HTML и записываем images в zip архив.
        html_local = crawl_result.html or ""
        zip_file.writestr("images/", "")  # Папка
        for img_src, content in media_images.items():
            img_src_parsed = UrlParser(img_src)
            img_src_hash = hash(img_src) % 1000000
            local_img_url = f"images/img_{img_src_hash}{img_src_parsed.get_extension()}"
            zip_file.writestr(local_img_url, content)
            html_local = html_local.replace(f'src="{img_src}"', f'src="{local_img_url}"')

        zip_file.writestr("local.html", html_local)

class CrawlArchiverConfig:
    def __init__(self,
                 browser_config: BrowserConfig,
                 run_config: CrawlerRunConfig,
                 make_local_html: bool = False):
        self.browser_config = browser_config
        self.run_config = run_config
        self.make_local_html = make_local_html

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

    async def crawl_and_archive_url(self, url: str) -> CrawlArchiverResult:
        """Обрабатывает один URL и возвращает ZIP buffer."""
        async with AsyncWebCrawler(config=self.config.browser_config) as crawler:
            result: CrawlResult = await crawler.arun(url=url, config=self.config.run_config)

        # Yield control, чтобы завершить все async операции crawler
        await asyncio.sleep(0)

        media_images = {}
        if self.config.make_local_html:
            media_images = await self.__get_media_images(result)

        # Yield control, чтобы завершить все async операции
        await asyncio.sleep(0)

        # Записываем результат в zip архив.
        return self.__zip_result_to_buffer(result, media_images)

    async def process_urls(self, urls: List[str]) -> List[CrawlArchiverResult]:
        """Обрабатывает массив URL параллельно."""
        tasks = [self.crawl_and_archive_url(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def __zip_result_to_buffer(self, crawl_result: CrawlResult, media_images: Dict[str, bytes]) -> CrawlArchiverResult:
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as zf:
            # Pdf
            self.writer.write_pdf(zf, crawl_result)
            # Screenshot
            self.writer.write_screenshot(zf, crawl_result)
            # Raw HTML
            self.writer.write_html(zf, crawl_result)
            # Local HTML
            self.writer.write_local_html(zf, crawl_result, media_images)
            # Meta JSON
            self.writer.write_meta(zf, crawl_result)

        zip_bytes = buffer.getvalue()
        return CrawlArchiverResult(crawl_result.url, zip_bytes)

    async def __get_media_images(self, crawl_result: CrawlResult) -> Dict[str, bytes]:
        if (not crawl_result.html
            or not crawl_result.media
            or "images" not in crawl_result.media):
            return {}

        # {src: image_bytes}
        img_map = {}
        url_joiner = UrlJoiner()

        async with aiohttp.ClientSession() as session:
            for img_info in crawl_result.media["images"]:
                src_img_url = img_info["src"]
                remote_img_url = url_joiner.join(crawl_result.url, src_img_url)
                async with session.get(remote_img_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        img_map[src_img_url] = content
        return img_map


