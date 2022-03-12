import os
import aiohttp


class OAuth:
    CLIENT_ID = '874663148374880287'
    BOT_TOKEN = os.getenv('DISCORD_TOKEN')
    STATE = CLIENT_ID[:5] + os.urandom(32).hex()
    CLIENT_SECRET = '7cC8YgIOb2RkkWft47ZNNkdsM9WFk6Nb'
    REDIRECT_URI = 'http://127.0.0.1:8000/'
    SCOPES = 'identify%20guilds'
    AUTH_URL = f'https://discord.com/api/oauth2/authorize?client_id=874663148374880287&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2F&response_type=code&scope={SCOPES}'
    TOKEN_URL = 'https://discord.com/api/oauth2/token'
    API_URL = 'https://discord.com/api/v10'

    @staticmethod
    async def get_access_token(code: str) -> dict:
        data = {
            'client_id': OAuth.CLIENT_ID,
            'client_secret': OAuth.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': OAuth.REDIRECT_URI,
            'scope': OAuth.SCOPES
        }
        async with aiohttp.ClientSession() as session:
            resp = await session.post(OAuth.TOKEN_URL, data=data)
            resp_dict = await resp.json()
        return resp_dict

    @staticmethod
    async def refresh_access_token(session: aiohttp.ClientSession, refresh_token: str) -> dict:
        data = {
            'client_id': OAuth.CLIENT_ID,
            'client_secret': OAuth.CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        resp = await session.post(OAuth.TOKEN_URL, data=data)
        resp_dict = await resp.json()
        return resp_dict

    @staticmethod
    async def get_user_info(access_token: str, session: aiohttp.ClientSession) -> dict:
        url = f'{OAuth.API_URL}/users/@me'
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = await session.get(url, headers=headers)
        return await resp.json()

    @staticmethod
    async def get_guilds(access_token: str, session: aiohttp.ClientSession) -> list:
        url = f'{OAuth.API_URL}/users/@me/guilds'
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = await session.get(url, headers=headers)
        return await resp.json()

    @staticmethod
    async def fetch_guild(session: aiohttp.ClientSession, guild_id: int) -> dict:
        url = f'{OAuth.API_URL}/guilds/{guild_id}'
        headers = {"Authorization": f"Bot {OAuth.BOT_TOKEN}"}
        resp = await session.get(url, headers=headers)
        return await resp.json()
