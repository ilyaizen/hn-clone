import asyncio
import aiohttp
from typing import List, Dict, Any
import traceback

from metadata import fetch_metadata
from database import update_stories

HACKER_NEWS_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKER_NEWS_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

async def fetch_json(session: aiohttp.ClientSession, url: str) -> Any:
    async with session.get(url) as response:
        return await response.json()

async def fetch_top_stories() -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        top_story_ids = await fetch_json(session, HACKER_NEWS_TOP_STORIES_URL)
        tasks = [
            fetch_json(session, HACKER_NEWS_ITEM_URL.format(story_id))
            for story_id in top_story_ids[:30]
        ]
        stories = await asyncio.gather(*tasks)
        return stories

async def start_scraper() -> None:
    while True:
        try:
            stories = await fetch_top_stories()
            stories_with_metadata = []
            for index, story in enumerate(stories, start=1):
                if 'url' in story:
                    metadata = await fetch_metadata(story['url'])
                    story.update(metadata)
                else:
                    story['description'] = ''
                    story['image_url'] = ''
                story['current_position'] = index
                story['hn_url'] = f"https://news.ycombinator.com/item?id={story['id']}"
                stories_with_metadata.append(story)
            await update_stories(stories_with_metadata)
            print(f"Updated {len(stories_with_metadata)} stories")
        except Exception as e:
            print(f"Error fetching stories: {e}")
            print("Traceback:")
            print(traceback.format_exc())
        await asyncio.sleep(180)  # Sleep for 3 minutes