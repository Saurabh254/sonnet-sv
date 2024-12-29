from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from . import auth


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials | None = await super(
                JWTBearer, self
            ).__call__(request)
            if credentials:
                if not credentials.scheme == "Bearer" and self.auto_error:
                    raise HTTPException(
                        status_code=401, detail="Invalid authentication scheme."
                    )
                if not self.verify_jwt(credentials.credentials) and self.auto_error:
                    raise HTTPException(
                        status_code=401, detail="Invalid token or expired token."
                    )
                return credentials.credentials
            else:
                if self.auto_error:
                    raise HTTPException(
                        status_code=401, detail="Invalid authorization code."
                    )
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        if not jwtoken:
            return isTokenValid

        try:
            payload = jwt.decode(jwtoken, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        except Exception:
            payload = None

        if payload:
            isTokenValid = True
        return isTokenValid
