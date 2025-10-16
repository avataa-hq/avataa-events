from sqlmodel import create_engine, Session
from fastapi import Depends
from fastapi.requests import Request
from config.database_config import DATABASE_URL
from services.security_service.security_data_models import UserData
from services.security_service.security_factory import security
from services.security_service.session.add_security import add_security_data

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=100,
)


def get_not_auth_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session


def get_session(request: Request, user_data: UserData = Depends(security)):
    with Session(engine, expire_on_commit=False) as session:
        add_security_data(session=session, request=request, user_data=user_data)
        yield session
