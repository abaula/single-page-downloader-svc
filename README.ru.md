# Single Page Downloader Service

[English version](README.md)

Single Page Downloader Service — это сервис для скачивания отдельных веб-страниц с использованием веб-скрейпинга, архивации в ZIP и предоставления доступа через gRPC API. Проект позволяет захватывать контент страницы, включая ресурсы, и возвращать его в удобном формате.

## Назначение проекта

Сервис предназначен для автоматизированного скачивания и архивации одной веб-страницы в ZIP-архив с помощью Crawl4ai для скрейпинга. Он предоставляет gRPC-интерфейс для интеграции в другие системы, упрощая обработку веб-контента.

Основная цель — создание шаблонного микросервиса, с возможностью дальнейшего расширения, для задач парсинга и хранения страниц в оффлайн-формате.

## Конфигурация (config/settings.yaml)

Файл `config/settings.yaml` определяет параметры сервиса, браузера и краулера. Пример конфигурации:

```yaml
max_workers: 10                     # Максимальное количество параллельных воркеров
grpc:
  service_port: 8000                # Порт gRPC-сервиса
  max_send_message_length: 52428800 # Максимальная длинна отправляемого сообщения gRPC - 50Mb
browser:                            # Смотрите настройки [Crawl4AI](https://docs.crawl4ai.com/) - BrowserConfig.
  headless: true                    # Запуск браузера в headless-режиме
  verbose: false                    # Отключить verbose-логи браузера
crawler:                            # Смотрите настройки [Crawl4AI](https://docs.crawl4ai.com/) - CrawlerRunConfig.
  cache_mode: "BYPASS"              # Режим кэша (BYPASS игнорирует кэш)
  capture_mhtml: true               # Захватывать MHTML
  screenshot: false                 # Отключить скриншоты
  pdf: false                        # Отключить PDF
  wait_for_images: true             # Ждать загрузки изображений
  verbose: false                    # Отключить verbose-логи краулера
```

Конфигурация загружается при запуске и позволяет настраивать производительность, режимы краулинга и браузера без перекомпиляции, при условии выноса папки config из контейнера на host, тогда изменения применяются при перезапуске сервиса.

## Технологии

- **Язык**: Python 3.10+.
- **API**: gRPC для высокопроизводительного RPC.
- **Веб-скрейпинг**: Crawl4ai — библиотека для извлечения контента страниц.
- **Архивация**: Zipfile — стандартная библиотека Python для создания ZIP-архивов.

Дополнительно используются стандартные библиотеки gRPC (grpcio, grpcio-tools) и зависимости из `requirements.txt`.

## Использованные компоненты

- **Crawl4ai**: Основной инструмент для парсинга HTML, CSS, JS и ресурсов страницы.
- **gRPC**: Для определения сервиса (proto-файлы генерируют stubs и сервер).
- **Zipfile**: Создание архивов скачанного контента.
- **Docker**: Контейнеризация для развертывания.
- **PyYAML**: Для чтения settings.yaml.
- Python-библиотеки: смотри файл `requirements.txt`.

## Как использовать Docker

1. Клонируйте репозиторий: `git clone https://github.com/abaula/single-page-downloader-svc.git && cd single-page-downloader-svc`.
2. Настройте `config/settings.yaml` (опционально).
3. Соберите образ: `docker build -t single-page-downloader-svc .`.
4. Запустите контейнер (пример с выносом настроек на host): `docker run -p 50001:8000 -v $(pwd)/config:/app/config single-page-downloader-svc`.
5. Подключитесь по gRPC к `localhost:50001` (используйте grpcurl или клиент).

## Вынос config на host (рекомендуется)
Чтобы редактировать конфигурацию без пересборки образа, используйте volume mount:

```bash
docker run -p 50001:8000 \
  -v $(pwd)/config:/app/config \
  single-page-downloader-svc
```

**Объяснение:**

`-v $(pwd)/config:/app/config` монтирует локальную папку `config/` в `/app/config` внутри контейнера.

Изменения в `settings.yaml` применяются при перезапуске контейнера

Полезно для dev/prod настройки без rebuild.

## gRPC API
Сервис предоставляет простой gRPC-интерфейс для скачивания страниц:

```protobuf
service PageDownloader {
  rpc DownloadPage (DownloadRequest) returns (DownloadResponse);
}

enum LoaderType {
  DYNAMIC = 0;  // Загрузка динамического контента
  STATIC = 1;   // Загрузка статического контента
}

message DownloadRequest {
  string url = 1;
  LoaderType loader_type = 2;
}

message DownloadResponse {
  string original_url = 1;   // Оригинальный URL запроса
  bytes zip_archive = 2;     // ZIP-архив с контентом страницы
}
```

Использование: Отправьте DownloadRequest с URL — получите DownloadResponse с ZIP-архивом, содержащим полученные ресурсы.

## Лицензия

GNU GPL 3.0 © 2026 \
Полный текст: [LICENSE](LICENSE)