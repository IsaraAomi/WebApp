import pytest

from api.schemas.task import TaskBase


def test_taskbase():
    taskbase = TaskBase(title="hoge")
    assert taskbase.model_dump() == {"title": "hoge"}
