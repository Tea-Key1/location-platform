import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_THIS_IN_RENDER")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID", "com.taikiyanada.roamie")
APPLE_ISSUER = "https://appleid.apple.com"
