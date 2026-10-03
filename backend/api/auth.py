from datetime import datetime, timedelta
from enum import Enum
import jwt
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "meowhere-secret-key-demo"
ALGORITHM = "HS256"

class Role(str, Enum):
    USER = "USER"
    STRAZ_MIEJSKA = "STRAZ_MIEJSKA"

class LoginRequest(BaseModel):
    username: str
    password: str

MOCK_USERS_DB = {
    "jan_kowalski": {"password": "123", "role": Role.USER, "name": "Jan Kowalski"},
    "straznik_piotr": {"password": "sm123", "role": Role.STRAZ_MIEJSKA, "name": "Patrol SM Ochota"}
}

security = HTTPBearer()

def create_access_token(username: str, role: Role) -> str:
    payload = {
        "sub": username,
        "role": role.value,
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy lub wygasły token"
        )

def require_role(required_role: Role):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Brak uprawnień. Zasób dostępny tylko dla Straży Miejskiej."
            )
        return current_user
    return checker

@router.post("/login")
def login(data: LoginRequest):
    """Logowanie zwracające token JWT z przypisaną rolą."""
    user = MOCK_USERS_DB.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=400, detail="Zły login lub hasło")

    token = create_access_token(data.username, user["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"]
    }
