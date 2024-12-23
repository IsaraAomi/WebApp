from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

"""
- Note:
    - Pydantic's "config":
        - It is used to customize model behavior and settings.
            - In particular, it is used to adjust rules for data validation and schema generation.
        - Role of Config and ConfigDict:
            - e.g.) data retrieval from attributes (ORM_MODE / from_attributes)
                - Used to convert ORM (Object-Relational Mapping) objects
                retrieved from a database directly into a Pydantic model.
        - In pydantic v2, the followings are not recommended:
            - In `Field()`, direct variables. (-> `json_schema_extra`)
            - In `Config` class, `orm_mode`. (-> `ConfigDict` and `from_attributes`)
"""


class TaskBase(BaseModel):
    """
    TaskBase.
    """

    title: Optional[str] = Field(None, json_schema_extra={"example": "クリーニングを取りに行く"})


class Task(TaskBase):
    """
    Task.

    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    done: bool = Field(False, json_schema_extra={"description": "完了フラグ"})


class TaskCreate(TaskBase):
    """
    TaskCreate.
    """

    pass


class TaskCreateResponse(TaskCreate):
    """
    TaskCreateResponse.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
