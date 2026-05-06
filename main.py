from src.config import load_settings
from src.pipeline import run_pipeline


def main() -> None:
    settings = load_settings()
    result = run_pipeline(settings)

    print(f"Fetched: {result['fetched']}")
    print(f"Selected: {result['selected']}")
    print(f"Published: {result['published']}")

    if result["skipped_reason"]:
        print(f"Skipped: {result['skipped_reason']}")


if __name__ == "__main__":
    main()
