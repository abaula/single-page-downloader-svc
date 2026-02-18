import asyncio
import signal
import grpc
from concurrent import futures
from page_downloader import LoaderType, PageDownloader, Request
import proto.page_downloader_pb2 as pb2
import proto.page_downloader_pb2_grpc as pb2_grpc
from dynaconf import Dynaconf

APP_ENVVAR_PREFIX = "APP_CRAWLARCHIVE"

class DownloaderService(pb2_grpc.PageDownloaderServicer):
    def __init__(self, settings: Dynaconf):
        super().__init__()
        self.settings = settings
        self.downloader = None

    async def DownloadPage(self, request: pb2.DownloadRequest, _) -> pb2.DownloadResponse:
        downloader_request = Request(url=request.url, loader_type=LoaderType(request.loader_type))
        downloader_result = await self.__get_downloader().download(downloader_request)
        response = pb2.DownloadResponse(original_url=downloader_result.original_url,
                                        zip_archive=downloader_result.zip_archive)
        return response

    def __get_downloader(self) -> PageDownloader:
        if not self.downloader:
            self.downloader = self.__create_downloader()
        return self.downloader

    def __create_downloader(self) -> PageDownloader:
        return PageDownloader(self.settings)

async def serve() -> None:
    settings = Dynaconf(
        envvar_prefix=APP_ENVVAR_PREFIX,
        settings_files=["config/settings.yaml"]
    )
    options = [("grpc.max_send_message_length", settings.grpc.max_send_message_length)]
    max_workers = settings.max_workers
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=max_workers), options=options)
    pb2_grpc.add_PageDownloaderServicer_to_server(
        DownloaderService(settings),
        server)
    grpc_service_port = settings.grpc.service_port
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