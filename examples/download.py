from pathlib import Path
from urllib.parse import urlparse
import tempfile
from dynaconf import Dynaconf
import grpc
import proto.page_downloader_pb2 as pb2
import proto.page_downloader_pb2_grpc as pb2_grpc

def get_archive_file_path(output_dir: Path, url: str) -> Path:
        output_dir.mkdir(exist_ok=True)
        url_parsed = urlparse(url)
        url_path = Path(url_parsed.path)
        zip_path = output_dir / f"{url_parsed.netloc}_{url_path.stem or "page"}.zip"
        return zip_path

def write_archive_to_file(output_dir: Path, url: str, buffer: bytes) -> Path:
    file_path = get_archive_file_path(output_dir, url)
    file_path.write_bytes(buffer)
    return file_path

settings = Dynaconf(
        envvar_prefix="APP_CRAWLARCHIVE",
        settings_files=["src/config/settings.yaml"]
    )

grpc_service_port = settings.grpc.service_port
channel = grpc.insecure_channel(f"localhost:{grpc_service_port}")
stub = pb2_grpc.PageDownloaderStub(channel)

request_url = "https://www.ixbt.com/"
request = pb2.DownloadRequest(url=request_url, loader_type=pb2.LoaderType.DYNAMIC) # type: ignore
#request_url = "https://old.mccme.ru/free-books/matpros/pdf/mp-34.pdf"
#request = pb2.DownloadRequest(url=request_url, loader_type=pb2.LoaderType.STATIC)

response = stub.DownloadPage(request)

tmp_path = Path(tempfile.gettempdir()) / "CRAWLARCHIVE"
file_path = write_archive_to_file(tmp_path, response.original_url, response.zip_archive)
print(f"Zip archive for {response.original_url} created:", str(file_path))
