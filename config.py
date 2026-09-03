import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ifisica-desenvolvimento")
    LOGO_URL = os.getenv(
        "LOGO_URL",
        "https://th.bing.com/th/id/R.b7e513ab9624989684162ee9f92e8a16"
        "?rik=NwdT6JD%2fLyvOPw&pid=ImgRaw&r=0"
    )
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
