from .bd import SessionLocal


async def get_bd():
    bd = SessionLocal()
    try:
        yield bd
    finally:
        bd.close()
