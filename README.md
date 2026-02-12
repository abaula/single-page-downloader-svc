# single-page-downloader-svc

Microservice for downloading a web page by specified URL with HTML and local resources preservation.

## Description

Implemented in Python. Uses **crawl4ai** library for efficient page downloading.

### Functionality
- Downloads **HTML** of the page unchanged.
- Creates **local-html** version: saves images to `images` folder, replaces links in HTML with local paths.
- Returns a ZIP archive with HTML and resources.

### Interface
**gRPC**:
- **Input**: Page URL (string).
- **Output**: URL + ZIP archive bytes.

## Installation and Running

1. Clone the repository:
   ```
   git clone https://github.com/your-username/single-page-downloader-svc.git
   cd single-page-downloader-svc
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the service:
   ```
   python main.py
   ```

## Working with Code

1. **Create virtual environment**:
   ```
   python -m venv venv
   # Linux/Mac:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

2. **Generate Protobuf code**:
   ```
   python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. ./proto/page_downloader.proto
   ```

3. **Install Playwright browsers** (for crawl4ai):
   ```
   playwright install chromium
   ```

## Usage

Example gRPC client (proto file in `proto/`):
```
service PageDownloader {
  rpc DownloadPage (DownloadRequest) returns (DownloadResponse);
}

message DownloadRequest {
  string url = 1;
}

message DownloadResponse {
  string original_url = 1;
  bytes zip_archive = 2;
}
```

## Technologies
- Python 3.10+
- Crawl4ai — for web scraping
- gRPC — for API
- Zipfile — for archiving

## License
GNU GPL 3.0 © 2026  \
Full text: [LICENSE](LICENSE)