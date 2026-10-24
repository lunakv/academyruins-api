import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def require_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    expected_user = os.environ.get("ADMIN_USER", "admin")
    expected_key = os.environ["ADMIN_KEY"]
    correct_user = secrets.compare_digest(credentials.username.encode(), expected_user.encode())
    correct_key = secrets.compare_digest(credentials.password.encode(), expected_key.encode())
    if not (correct_user and correct_key):
        raise HTTPException(401, "Incorrect admin credentials", headers={"WWW-Authenticate": "Basic"})
