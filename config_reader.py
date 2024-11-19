from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    token: str

@dataclass
class Settings:
    bots: Bots


def Config(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            token=env.str("BOT_TOKEN"),
        )
    )


config = Config(".env")
