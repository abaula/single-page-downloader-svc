import asyncio
import signal
import grpc
from concurrent import futures
import page_downloader_pb2
import page_downloader_pb2_grpc
from dynaconf import Dynaconf
from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig
from crawler import CrawlArchiverConfig, CrawlArchiveWriter, CrawlArchiver

APP_ENVVAR_PREFIX = "APP_CRAWLARCHIVE"

class DownloaderService(page_downloader_pb2_grpc.PageDownloaderServicer):
    def __init__(self, settings: Dynaconf):
        super().__init__()
        self.settings = settings

    async def DownloadPage(self, request, context):
        zip_content_writer = CrawlArchiveWriter()
        browser_config = BrowserConfig(headless=self.settings.browser.headless,
                                    verbose=self.settings.browser.verbose)
        run_config = CrawlerRunConfig(
                        capture_mhtml=self.settings.crawler.capture_mhtml,
                        screenshot=self.settings.crawler.screenshot,
                        pdf=self.settings.crawler.pdf,
                        cache_mode=CacheMode[self.settings.crawler.cache_mode],
                        verbose=self.settings.crawler.verbose,
                        wait_for_images=self.settings.crawler.wait_for_images
                    )
        config = CrawlArchiverConfig(browser_config=browser_config,
                                    run_config=run_config)
        archiver = CrawlArchiver(config=config,
                                writer=zip_content_writer)

        result = await archiver.crawl_and_archive_url(request.url)
        response = page_downloader_pb2.DownloadResponse()
        response.original_url = result.url
        response.zip_archive = result.zip_buffer
        return response

async def serve() -> None:
    settings = Dynaconf(
        envvar_prefix=APP_ENVVAR_PREFIX,
        settings_files=["config/settings.yaml"]
    )
    grpc_service_port = settings.grpc_service_port
    max_workers = settings.max_workers
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    page_downloader_pb2_grpc.add_PageDownloaderServicer_to_server(
        DownloaderService(settings), server)
    server.add_insecure_port(f"[::]:{grpc_service_port}")
    await server.start()
    print(f"Async gRPC server running on port {grpc_service_port}")

    # Graceful shutdown SIGINT/SIGTERM
    shutdown_event = asyncio.Event()

    def signal_handler():
        print("Completion signal received")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await shutdown_event.wait()
    finally:
        # Graceful stop 5-sec timeout
        await server.stop(5)
        print("The server has stopped")

if __name__ == '__main__':
    asyncio.run(serve())