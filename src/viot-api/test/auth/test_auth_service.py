from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BadRequestException, UnauthorizedException
from app.modules.auth import schemas
from app.modules.auth.schemas import LoginRequest


async def test_authenticate(db: AsyncSession):
    from app.modules.auth.service import authenticate, create

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"
    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    await create(db=db, request=request)

    login_request = LoginRequest(email=email, password=password)
    authenticated_user = await authenticate(db=db, request=login_request)

    assert authenticated_user.email == email
    assert authenticated_user.first_name == first_name
    assert authenticated_user.last_name == last_name


async def test_authenticate_wrong_password(db: AsyncSession):
    from app.modules.auth.service import authenticate, create

    email = "abc@gmail.com"
    password = "!123QWEqwe"
    first_name = "John"
    last_name = "Doe"
    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    await create(db=db, request=request)

    login_request = LoginRequest(email=email, password="!123QWEwrong")

    with pytest.raises(UnauthorizedException) as excinfo:
        await authenticate(db=db, request=login_request)

    assert str(excinfo.value) == "Wrong password"


async def test_exist_by_email(db: AsyncSession):
    from app.modules.auth.service import create, exist_by_email

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"
    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    await create(db=db, request=request)

    assert await exist_by_email(db=db, email=email) is True


async def test_register_user_already_exists(db: AsyncSession):
    from app.modules.auth.service import create, register

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"

    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    await create(db=db, request=request)

    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    with pytest.raises(BadRequestException) as excinfo:
        await register(db=db, request=request)

    assert str(excinfo.value) == "User with email abc@gmail.com already exists"


async def test_create_user(db: AsyncSession):
    from app.modules.auth.service import create

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"
    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await create(db=db, request=request)

    assert user.email == email
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.disabled is False
    assert user.role == "User"


async def test_update_user(db: AsyncSession):
    from app.modules.auth.service import create, update

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"

    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await create(db=db, request=request)

    new_first_name = "Jane"
    new_last_name = "Doe"

    request = schemas.UserUpdateRequest(first_name=new_first_name, last_name=new_last_name)
    updated_user = await update(db=db, request=request, user_id=user.id)

    assert updated_user.email == email
    assert updated_user.first_name == new_first_name
    assert updated_user.last_name == new_last_name
    assert updated_user.disabled is False


async def test_delete_user(db: AsyncSession):
    from app.modules.auth.service import create, delete, get_or_raise

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"

    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await create(db=db, request=request)

    await delete(db=db, user_id=user.id)

    try:
        await get_or_raise(db=db, user_id=user.id)
    except Exception as e:
        assert str(e) == "User with this id not exist."


async def test_exist_by_id(db: AsyncSession):
    from app.modules.auth.service import create, exist_by_id

    email = "abc@gmail.com"
    password = "!@#123QWEqwe"
    first_name = "John"
    last_name = "Doe"

    request = schemas.RegisterRequest(
        email=email, password=password, first_name=first_name, last_name=last_name
    )
    user = await create(db=db, request=request)

    assert await exist_by_id(db=db, id=user.id) is True
    assert await exist_by_id(db=db, id=uuid4()) is False
