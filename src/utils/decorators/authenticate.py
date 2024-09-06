from functools import wraps

def authenticate(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        cls = args[0]
        session = args[1]
        session.headers["Authorization"] = f"Bearer {cls._token}"
        return await fn(*args, **kwargs)
    return wrapper

