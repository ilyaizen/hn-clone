from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
from typing import AsyncGenerator
from datetime import datetime

from hn_scraper import start_scraper
from database import get_stories, init_db

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

async def lifespan(app: FastAPI) -> AsyncGenerator:
    await init_db()
    app.state.scraper_task = asyncio.create_task(start_scraper())
    yield
    app.state.scraper_task.cancel()

def time_ago(dt: datetime) -> str:
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} year{'s' if diff.days >= 730 else ''} ago"
    if diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days >= 60 else ''} ago"
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    if diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour{'s' if diff.seconds >= 7200 else ''} ago"
    if diff.seconds > 60:
        return f"{diff.seconds // 60} minute{'s' if diff.seconds >= 120 else ''} ago"
    return f"{diff.seconds} second{'s' if diff.seconds > 1 else ''} ago"

def get_trend_symbol(trend: str) -> str:
    return {'up': '▲', 'down': '▼'}.get(trend, '')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    stories = await get_stories()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stories": stories,
            "time_ago": time_ago,
            "get_trend_symbol": get_trend_symbol,
        },
    )