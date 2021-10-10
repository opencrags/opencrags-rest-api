from pathlib import Path
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    openid_connect_url: str = Field(..., env="AUTH_OPENID_CONNECT_URL")
    issuer: str = Field(..., env="AUTH_ISSUER")
    client_id: str = Field(..., env="AUTH_CLIENT_ID")

    users_url: str = Field(..., env="ADMIN_USERS_URL")

    database_url: str = Field(..., env="DB")


config = Config()

if not config.images_directory.exists():
    config.images_directory.mkdir()
