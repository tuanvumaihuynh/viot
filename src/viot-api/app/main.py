import logging

import uvicorn

from app.bootstrap import create_app
from app.config import app_settings
from app.log import init_logger

init_logger()

logger = logging.getLogger(__name__)

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=app_settings.VIOT_API_PORT,
        server_header=False,
        date_header=False,
        log_config=None,
        reload=app_settings.IS_DEV_ENV,
    )
