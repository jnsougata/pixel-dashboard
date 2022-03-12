from typing import Any, Union, List, Dict
from deta import Deta


class DB:
    def __init__(self, token: str):
        self.deta = Deta(token)

    async def put(self, guild_id: int, item: Any, key: str):
        base = self.deta.Base(f'GUILD{guild_id}')
        return base.put({'item': item}, key)

    async def get(self, guild_id: int, key: str):
        base = self.deta.Base(f'GUILD{guild_id}')
        raw = base.get(key)
        if raw:
            return raw['item']
        return None


class Cache:
    def __init__(self):
        self.chunks = {}

    def store(self, key: str, chunk_data: Any):
        self.chunks[key] = chunk_data
        return chunk_data

    def get(self, key) -> Any:
        return self.chunks.get(key)

    def delete(self, chunk_id):
        return self.chunks.pop(chunk_id, None)


class User:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.name = data.get('username')
        self.email = data.get('email')
        self.avatar = data.get('avatar')
        self.mfa_enabled = data.get('mfa_enabled')
        self.banner = data.get('banner')
        self.bot = data.get('bot')
        self.locale = data.get('locale')
        self.flags = data.get('flags')
        self.discriminator = data.get('discriminator')
        self.accent_color = data.get('accent_color')
        self.premium_type = data.get('premium_type')
        self.public_flags = data.get('public_flags')


class PartialGuild:

    def __init__(self, data: dict):
        self.id = int(data.get('id'))
        self.name = data.get('name')
        self.icon = data.get('icon')
        self.is_owner = data.get('owner')
        self.permissions = int(data.get('permissions'))
        self.features = data.get('features')
        self.can_manage = (1 << 5 | self.permissions) == self.permissions


class Guild:

    def __init__(self, data: dict):
        self.id = int(data.get('id'))
        self.name = data.get('name')
        self.icon = f"https://cdn.discordapp.com/icons/{self.id}/{data.get('icon')}.png?size=1024"
        self.roles = data.get('roles')
        self.channels = data.get('channels')
