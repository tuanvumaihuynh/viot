from typing import Annotated

from fastapi import Query
from pydantic import StringConstraints

NameStr = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z ]+$", strip_whitespace=True, min_length=2, max_length=20),
]
NameWithNumberStr = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-zA-Z0-9 ]+$", strip_whitespace=True, min_length=4, max_length=32
    ),
]
TeamSlug = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-z0-9]+(?:(?:-|_)+[a-z0-9]+)*$",
        strip_whitespace=True,
        min_length=1,
        max_length=50,
    ),
]
QueryStr = Annotated[str, StringConstraints(pattern=r"^[ -~]+$", min_length=1)]


# Paging
PageQuery = Annotated[
    int, Query(ge=1, alias="page", description="Maximum amount of entities in a one page")
]
PageSizeQuery = Annotated[
    int,
    Query(ge=1, le=50, alias="pageSize", description="Sequence number of page starting from 0"),
]
