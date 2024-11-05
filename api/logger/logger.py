import logging

formatter = logging.Formatter('%(levelname)s      %(asctime)s - %(name)s - %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers.clear()
uvicorn_access_handler = logging.StreamHandler()
uvicorn_access_handler.setFormatter(formatter)
uvicorn_access_logger.addHandler(uvicorn_access_handler)

uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.handlers.clear()
uvicorn_error_handler = logging.StreamHandler()
uvicorn_error_handler.setFormatter(formatter)
uvicorn_error_logger.addHandler(uvicorn_error_handler)
