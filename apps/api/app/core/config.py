import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_THIS_IN_RENDER")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7