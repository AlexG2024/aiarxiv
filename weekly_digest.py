from src.config import load_settings
from src.digest import build_weekly_digest
from src.storage import load_history


def main() -> None:
    settings = load_settings()
    history = load_history(settings.history_storage_path)
    print(build_weekly_digest(history))


if __name__ == "__main__":
    main()
