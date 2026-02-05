import pytest
from fastapi import FastAPI

from src.main import bootstrap
from src.core.config import get_config

integration = pytest.mark.integration


@integration
def test_app_is_created_successfully() -> None:
    app = bootstrap()

    assert isinstance(app, FastAPI)


@integration
def test_app_has_correct_name_and_version() -> None:
    config = get_config()
    app = bootstrap()

    assert app.title == config.APP_NAME
    assert app.version == config.VERSION
