"""Convoq entry point."""

import logging
import sys

from dotenv import load_dotenv

from convoq.core.engine import ConvoqEngine


def main() -> None:
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    logger = logging.getLogger("convoq")
    logger.info("Convoq v0.1.0 starting...")

    try:
        engine = ConvoqEngine()
        engine.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
