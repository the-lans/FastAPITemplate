# to get a string like this run: openssl rand -hex 32
SECRET_KEY = "e0d7fc931d76f1e2a7006e30d7a4c7273a4d95f2e56496f61bcb72be5ae7ec11"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
DOMAIN = "localhost"

users_db = {
    "test": {
        "username": "test",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$x6xslzyP/BfwRXzEjg7mOOCVRRbui.l418.FsiGW613uHE232F20e",  # test
        "disabled": False,
    }
}
