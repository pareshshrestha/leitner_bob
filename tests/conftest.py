#!python3

import pytest
from app.app_logging import get_logger

@pytest.fixture(scope='session', autouse=True)
def configure_logging():
	get_logger('tests')
