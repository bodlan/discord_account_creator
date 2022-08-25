import os


class CONFIG:
    DISCORD_SITE = "https://discord.com/register"
    DISCORD_SITE_API = "https://discord.com/api/v9/auth/register"
    DISCORD_SITE_KEY = "4c672d35-0701-42b2-88c3-78380b0db560"
    CAPTCHA_API_KEY = os.getenv("API_KEY")
