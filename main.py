import os
import models
import fastapi
import aiohttp
import aiotube
from oauth import OAuth
from fastapi import FastAPI, Request
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


app = FastAPI()
app.cache = models.Cache()
app.db = models.DB(os.getenv('DETA_TOKEN'))
app.mount("/static", StaticFiles(directory="static"), name="static")
pages = Jinja2Templates(directory="pages")


@app.get("/login", response_class=HTMLResponse)
async def login():
    return RedirectResponse(OAuth.AUTH_URL)


@app.get("/invite", response_class=HTMLResponse)
async def invite():
    return fastapi.responses.RedirectResponse(
        f'https://discord.com/api/oauth2/authorize?client_id={OAuth.CLIENT_ID}'
        f'&permissions=2147993600&scope=bot%20applications.commands')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, code: Optional[str] = None):
    if code:
        return RedirectResponse(url=f'/redirect/{code}')
    return pages.TemplateResponse("root.html", {"request": request, "auth_url": OAuth.AUTH_URL})


@app.get("/redirect/{code}", response_class=HTMLResponse)
async def redirect(request: Request, code: str):
    if code:
        try:
            data = await OAuth.get_access_token(code)
            token = data["access_token"]
            app.cache.store(code, token)
            async with aiohttp.ClientSession() as session:
                user_info = await OAuth.get_user_info(token, session)
                user = models.User(user_info)
                avatar = f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.png?size=1024"
                guild_resource = await OAuth.get_guilds(token, session)
                guilds = [models.PartialGuild(guild) for guild in guild_resource]
                guild_zip = [(guild.name, guild.id) for guild in guilds if guild.can_manage]
                szip = sorted(guild_zip, key=lambda x: x[0].lower())
            return pages.TemplateResponse(
                "redirect.html",
                {
                    "token": token, "request": request, "avatar_url": avatar,
                    "code": code, "tag_elements": szip, "user_name": user.name.capitalize(),
                }
            )
        except Exception as e:
            return RedirectResponse(url=f'/login')


@app.get("/dashboard/{server_id}/{auth_code}/{token}", response_class=HTMLResponse)
async def dashboard(request: Request, server_id: int, auth_code: str, token: str):
    cached_token = app.cache.get(auth_code)
    if not cached_token:
        return RedirectResponse(url=f'/')
    elif cached_token and cached_token != token:
        app.cache.delete(auth_code)
        return RedirectResponse(url=f'/')

    async with aiohttp.ClientSession() as session:
        info = await OAuth.fetch_guild(session, server_id)
        if 'code' not in info:
            guild = models.Guild(info)
            icon = f"https://cdn.discordapp.com/icons/{server_id}/{info['icon']}.png?size=1024"
            return pages.TemplateResponse(
                "dashboard.html",
                {"request": request, "guild": guild, "code": auth_code, "token": token}
            )
        else:
            return RedirectResponse(url=f'/invite')


@app.get("/{server_id}/youtube/{auth_code}/{token}", response_class=HTMLResponse)
async def dashboard_youtube(request: Request, server_id: int, auth_code: str, token: str):
    cached_token = app.cache.get(auth_code)
    if not cached_token:
        return RedirectResponse(url=f'/')
    elif cached_token and cached_token != token:
        app.cache.delete(auth_code)
        return RedirectResponse(url=f'/')
    async with aiohttp.ClientSession() as session:
        info = await OAuth.fetch_guild(session, server_id)
        if 'code' not in info:
            guild = models.Guild(info)
            icon = f"https://cdn.discordapp.com/icons/{server_id}/{info['icon']}.png?size=1024"
    channels = await app.db.get(server_id, 'youtube')
    if not channels:
        pass
    else:
        channel_ids = list(channels.keys())
        receivers = await app.db.get(server_id, 'receivers')
        ch_info = [aiotube.Channel(channel_id).info for channel_id in channel_ids]
        return pages.TemplateResponse(
            "youtube.html",
            {"request": request, "guild": guild, "code": auth_code,
             "token": token, "all_info": ch_info, "receivers": receivers}
        )
