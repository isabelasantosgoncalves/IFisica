import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

VARIAVEIS_OBRIGATORIAS = ("DB_HOST", "DB_PORT", "DB_USER", "DB_NAME")


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
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))

    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


def conferir_configuracao():
    faltando = [
        nome for nome in VARIAVEIS_OBRIGATORIAS
        if not getattr(Config, nome)
    ]

    if faltando:
        raise RuntimeError(
            "Faltam variáveis no arquivo .env: " + ", ".join(faltando) + ". "
            "Copie o .env.example e preencha com os dados do servidor de banco."
        )

    if Config.SECRET_KEY == "ifisica-desenvolvimento":
        raise RuntimeError(
            "Defina SECRET_KEY no .env. Gere uma com: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
