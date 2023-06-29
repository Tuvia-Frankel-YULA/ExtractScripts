import asyncio


def is_true_complex(val) -> bool:
    return isinstance(val, bool) and val \
        or isinstance(val, int) and val > 0 \
        or isinstance(val, float) and val > 0 \
        or str(val).lower() == 't' \
        or str(val).lower() == 'true' \
        or str(val).lower() == 'y' \
        or str(val).lower() == 'yes'


def run_sync(coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


def uri_to_path(uri: str) -> str:
    if uri.startswith('file://'):
        return uri.removeprefix('file://')
    else:
        raise Exception("Unsupported uri type!")
