from __future__ import annotations

import logging
import sys

from app.core.config import bootstrap_files
from app.storage.paths import ERROR_LOG_PATH, ensure_directories


def setup_logging() -> None:
    ensure_directories()
    logging.basicConfig(
        filename=ERROR_LOG_PATH,
        filemode="a",
        level=logging.ERROR,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main() -> int:
    setup_logging()
    bootstrap_files()

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print("PySide6 is not installed. Install dependencies: pip install -r requirements.txt")
        logging.error("PySide6 import failed. Install dependencies from requirements.txt")
        return 1

    from app.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
