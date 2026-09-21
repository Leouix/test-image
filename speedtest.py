#!/usr/bin/env python3
"""Замер скорости интернета: несколько последовательных загрузок файла по URL."""

import argparse
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "https://asialive.news/test-image"
DEFAULT_RUNS = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT = 60

HEADERS = {
    "User-Agent": "Mozilla/5.0 (speedtest.py)",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def download_once(url):
    """Один запрос: возвращает (байты, секунды). Тело вычитывается полностью."""
    req = urllib.request.Request(url, headers=HEADERS)
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        if resp.status != 200:
            raise urllib.error.HTTPError(
                url, resp.status, resp.reason, resp.headers, None
            )
        size = 0
        while chunk := resp.read(CHUNK_SIZE):
            size += len(chunk)
    elapsed = time.perf_counter() - start
    return size, elapsed


def main():
    parser = argparse.ArgumentParser(description="Замер скорости интернета по URL.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="URL файла для загрузки")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help="число запросов")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs должен быть >= 1")

    print(f"URL: {args.url}")
    print(f"Запросов: {args.runs}")
    print("-" * 48)

    total_bytes = 0
    total_time = 0.0
    ok_runs = 0

    for i in range(1, args.runs + 1):
        try:
            size, elapsed = download_once(args.url)
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            print(f"#{i:02d}  ошибка: {exc}")
            continue

        ok_runs += 1
        total_bytes += size
        total_time += elapsed
        mb = size / 1_000_000
        speed = size / elapsed / 1_000_000 if elapsed > 0 else 0.0
        print(f"#{i:02d}  {mb:6.2f} MB  {elapsed:6.2f} s  {speed:7.2f} MB/s")

    print("-" * 48)
    if ok_runs == 0:
        print("Все запросы завершились ошибкой.")
        return 1

    avg_time = total_time / ok_runs
    avg_speed = total_bytes / total_time / 1_000_000 if total_time > 0 else 0.0

    print(f"Успешных запросов:      {ok_runs}/{args.runs}")
    print(f"Скачано всего:          {total_bytes / 1_000_000:.2f} MB")
    print(f"Среднее время запроса:  {avg_time:.2f} s")
    print(f"Средняя скорость:       {avg_speed:.2f} MB/s ({avg_speed * 8:.2f} Mbit/s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
