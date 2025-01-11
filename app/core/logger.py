import logging


logging.basicConfig(
    level=logging.INFO,  # Set the default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="[%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("../televito.log", mode="a", encoding="utf-8"),
    ],
)
televito_logger = logging.getLogger("televito_bot")
