from src.config import load_settings
from src.pipeline import publish_due_post


def main() -> None:
    settings = load_settings()
    result = publish_due_post(settings)

    print(f"Published: {result['published']}")
    if result["published_title"]:
        print(f"Title: {result['published_title']}")
    if result["skipped_reason"]:
        print(f"Skipped: {result['skipped_reason']}")


if __name__ == "__main__":
    main()
