from contextvars import ContextVar

from fastapi import BackgroundTasks, Depends, Request, Response

request_ctx: ContextVar[Request | None] = ContextVar("request_ctx", default=None)
response_ctx: ContextVar[Response | None] = ContextVar("response_ctx", default=None)
background_task_ctx: ContextVar[BackgroundTasks | None] = ContextVar(
    "background_task_ctx", default=None
)


# Warning: Need to use async function to make it work
async def _get_request_ctx(request: Request):
    token = request_ctx.set(request)
    yield
    request_ctx.reset(token)


async def _get_response_ctx(response: Response):
    token = response_ctx.set(response)
    yield
    response_ctx.reset(token)


async def _get_background_task_ctx(background_tasks: BackgroundTasks):
    token = background_task_ctx.set(background_tasks)
    yield
    background_task_ctx.reset(token)


ResponseCtxDependency = Depends(_get_response_ctx)
BackgroundTaskCtxDependency = Depends(_get_background_task_ctx)
RequestCtxDependency = Depends(_get_request_ctx)
