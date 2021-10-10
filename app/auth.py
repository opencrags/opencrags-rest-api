from fastapi_third_party_auth import Auth, GrantType

from app.config import config


auth = Auth(
    openid_connect_url=config.openid_connect_url,
    issuer=config.issuer,
    client_id=config.client_id,
    grant_types=[GrantType.IMPLICIT],
)
