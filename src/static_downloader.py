import datetime
from io import BytesIO
import io
import json
from yarl import URL
import os
from urllib.parse import unquote, urlparse
from zipfile import ZIP_DEFLATED, ZipFile
import aiohttp

def json_serializable(obj):
    if isinstance(obj, URL):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (io.BytesIO, bytes)):
        return obj.getvalue().decode('utf-8') if hasattr(obj, 'getvalue') else obj.decode('utf-8')
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

class DownloadResponse:
    def __init__(self,
                 url: str,
                 zip_buffer: bytes):
        self.url = url
        self.zip_buffer = zip_buffer

class StaticContentArchiver:
    async def download(self, url: str) -> DownloadResponse:
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zf:
            await self.__get_and_write_content(url, zf)
        return DownloadResponse(url, zip_buffer.getvalue())

    async def __get_and_write_content(self, url: str, zip_file: ZipFile):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                self.__write_meta(zip_file, response)
                content_name = self.__get_entry_name_from_url(url)
                await self.__write_content(content_name, zip_file, response)

    async def __stream_to_bytesio(self, reader: aiohttp.StreamReader) -> BytesIO:
        buffer = BytesIO()
        chunk = await reader.read(8192)
        while chunk:
            buffer.write(chunk)
            chunk = await reader.read(8192)
        buffer.seek(0)
        return buffer

    async def __write_content(self, content_name: str, zip_file: ZipFile, response: aiohttp.ClientResponse):
        """
        Raw content
        """
        content_buffer = await self.__stream_to_bytesio(response.content)
        zip_file.writestr(content_name, content_buffer.getvalue())

    def __write_meta(self, zip_file: ZipFile, response: aiohttp.ClientResponse):
        """
        Metadata metadata.json
        """
        meta = {
            "url": response.url,
            "response_headers": dict(getattr(response, "headers", {}))
        }
        zip_file.writestr("metadata.json", json.dumps(meta, default=json_serializable, indent=2, ensure_ascii=False))

    def __get_entry_name_from_url(self, url: str, default: str = "content"):
        try:
            parsed = urlparse(url)
            entry_name = os.path.basename(unquote(parsed.path).split('?')[0])
            return entry_name
        except:
            return default