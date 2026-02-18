# Single Page Downloader Service

[Русская версия](README.ru.md)

Single Page Downloader Service is a service for downloading individual web pages using web scraping, archiving them into ZIP files, and providing access via a gRPC API. The project allows capturing a page’s content—including its resources—and returning it in a convenient format.

## Project Purpose

The service is designed for automated downloading and archiving of a single web page into a ZIP archive using Crawl4ai for scraping. It provides a gRPC interface for integration with other systems, simplifying web content processing.

The main goal is to create a template microservice—easily extensible in the future—for tasks involving parsing and offline storage of web pages.

## Configuration (config/settings.yaml)

The `config/settings.yaml` file defines parameters for the service, browser, and crawler. Example configuration:

```yaml
max_workers: 10                     # Maximum number of parallel workers
grpc:
  service_port: 8000                # gRPC service port
  max_send_message_length: 52428800 # The maximum length of a gRPC message sent is 50 MB.
browser:                            # See [Crawl4AI](https://docs.crawl4ai.com/) - BrowserConfig.
  headless: true                    # Run the browser in headless mode
  verbose: false                    # Disable verbose browser logs
crawler:                            # See [Crawl4AI](https://docs.crawl4ai.com/) - CrawlerRunConfig.
  cache_mode: "BYPASS"              # Cache mode (BYPASS ignores cache)
  capture_mhtml: true               # Capture MHTML
  screenshot: false                 # Disable screenshots
  pdf: false                        # Disable PDF capture
  wait_for_images: true             # Wait for images to load
  verbose: false                    # Disable verbose crawler logs
```

The configuration loads at startup and allows tuning of performance, crawling, and browser modes without recompiling the image. If the `config` folder is mounted to the host, changes apply upon service restart.

## Technologies

- **Language**: Python 3.10+
- **API**: gRPC for high-performance RPC
- **Web scraping**: Crawl4ai — library for page content extraction
- **Archiving**: Zipfile — Python standard library for creating ZIP archives

Additionally, standard gRPC libraries (`grpcio`, `grpcio-tools`) and dependencies from `requirements.txt` are used.

## Components Used

- **Crawl4ai** – main tool for parsing HTML, CSS, JS, and page resources
- **gRPC** – defines the service; proto files generate stubs and server code
- **Zipfile** – handles content archiving
- **Docker** – containerization for deployment
- **PyYAML** – for reading `settings.yaml`
- Python libraries: see `requirements.txt`

## Using Docker

1. Clone the repository:
   `git clone [https://github.com/abaula/single-page-downloader-svc.git](https://github.com/abaula/single-page-downloader-svc.git) && cd single-page-downloader-svc`
2. Optionally, configure `config/settings.yaml`
3. Build the image:
   `docker build -t single-page-downloader-svc .`
4. Run the container (with settings mounted from host):
   `docker run -p 50001:8000 -v $(pwd)/config:/app/config single-page-downloader-svc`
5. Connect via gRPC to `localhost:50001` (using grpcurl or a client)

## Mounting config to host (recommended)

To edit configuration without rebuilding the image, use a volume mount:

```bash
docker run -p 50001:8000 \
  -v $(pwd)/config:/app/config \
  single-page-downloader-svc
```

**Explanation:**

`-v $(pwd)/config:/app/config` mounts the local `config/` folder into `/app/config` inside the container.

Changes to `settings.yaml` apply when restarting the container.

Useful for dev/prod environments without rebuilds.

## gRPC API

The service provides a simple gRPC interface for downloading pages:

```protobuf
service PageDownloader {
  rpc DownloadPage (DownloadRequest) returns (DownloadResponse);
}

enum LoaderType {
  DYNAMIC = 0;  // Loading dynamic content
  STATIC = 1;   // Loading static content
}

message DownloadRequest {
  string url = 1;
  LoaderType loader_type = 2;
}

message DownloadResponse {
  string original_url = 1;   // Original request URL
  bytes zip_archive = 2;     // ZIP archive containing the page content
}
```

Usage: Send a `DownloadRequest` with a URL — receive a `DownloadResponse` containing a ZIP archive of the retrieved resources.

## License

GNU GPL 3.0 © 2026 \
Full text: [LICENSE](LICENSE)
