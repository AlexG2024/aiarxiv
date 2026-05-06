from src.config import load_settings
from src.pipeline import build_daily_queue


def main() -> None:
    settings = load_settings()
    result = build_daily_queue(settings)

    print(f"Fetched: {result['fetched']}")
    print(f"Selected: {result['selected']}")
    print(f"Queue status: {result['queue_status']}")

    if result["skipped_reason"]:
        print(f"Skipped: {result['skipped_reason']}")


if __name__ == "__main__":
    main()
