import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Change logging level to DEBUG for more detailed logs
    #level=logging.INFO
)

logger = logging.getLogger("FaultMaven")