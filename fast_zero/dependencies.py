from typing import Annotated

from fastapi import Query

from fast_zero.models import TodoState
from fast_zero.schemas import TodoFilters


def get_filters(
    title: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    state: Annotated[TodoState | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
) -> TodoFilters:
    return TodoFilters(
        title=title,
        description=description,
        state=state,
        offset=offset,
        limit=limit,
    )
