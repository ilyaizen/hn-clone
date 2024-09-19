from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from models import Base, Story
from sqlalchemy.engine import URL
from datetime import datetime

DATABASE_URL = URL.create(
    "sqlite+aiosqlite",
    database="hn_clone.db",
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully")

async def get_stories() -> List[Story]:
    async with async_session() as session:
        result = await session.execute(
            select(Story).where(Story.current_position.isnot(None)).order_by(Story.current_position)
        )
        return result.scalars().all()

async def update_stories(new_stories: List[Dict[str, Any]]) -> None:
    async with async_session() as session:
        existing_stories = (await session.execute(select(Story))).scalars().all()
        existing_ids = {story.id for story in existing_stories}
        new_ids = {story['id'] for story in new_stories}

        # Handle removed stories
        for story_id in existing_ids - new_ids:
            story = await session.get(Story, story_id)
            if story:
                story.last_position = story.current_position
                story.current_position = None
                story.trend = 'same'
                session.add(story)

        for new_story in new_stories:
            # Convert fields
            new_story['poster'] = new_story.pop('by', None)
            new_story['comments_count'] = new_story.pop('descendants', None)
            new_story['time_posted'] = datetime.fromtimestamp(new_story.pop('time', 0))
            new_story['text'] = new_story.get('text')

            # Remove unnecessary fields
            new_story.pop('kids', None)
            new_story.pop('type', None)

            existing_story = await session.get(Story, new_story['id'])
            if existing_story:
                new_story['last_position'] = existing_story.current_position
                new_story['trend'] = determine_trend(
                    existing_story.current_position, new_story['current_position']
                )
                for key, value in new_story.items():
                    setattr(existing_story, key, value)
                session.add(existing_story)
            else:
                new_story['last_position'] = None
                new_story['trend'] = 'same'
                story = Story(**new_story)
                session.add(story)
        await session.commit()
        print("Stories updated successfully")

def determine_trend(last_pos: int, current_pos: int) -> str:
    if last_pos is None or last_pos == current_pos:
        return 'same'
    return 'up' if last_pos > current_pos else 'down'