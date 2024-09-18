import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any
from PIL import Image
from io import BytesIO
import os
import hashlib
import asyncio
from ssl import SSLError

metadata_cache: Dict[str, Dict[str, Any]] = {}
IMAGE_DIR = "static/images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

async def fetch_metadata(url: str) -> Dict[str, Any]:
    if url in metadata_cache:
        return metadata_cache[url]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10, ssl=False) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"HTTP error {response.status}",
                    )
                html = await response.text()
        
        soup = BeautifulSoup(html, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        og_description = soup.find('meta', property='og:description')
        favicon = soup.find('link', rel='icon')
        image_url = og_image['content'] if og_image else (favicon['href'] if favicon else None)
        description = og_description['content'] if og_description else ''
        
        # Truncate description if it's too long
        description = description[:280].rsplit(' ', 1)[0] + '...' if len(description) > 280 else description
        
        base_url = f"{response.url.scheme}://{response.url.host}"
        image_filename = await download_and_resize_image(image_url, base_url) if image_url else None
        
        metadata = {
            'image_url': f"/static/images/{image_filename}" if image_filename else None,
            'description': description,
        }
        metadata_cache[url] = metadata
        return metadata
    except (aiohttp.ClientError, asyncio.TimeoutError, SSLError) as e:
        print(f"Error fetching metadata for {url}: {e}")
        return {'image_url': None, 'description': f"Error fetching metadata: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error fetching metadata for {url}: {e}")
        return {'image_url': None, 'description': f"Unexpected error: {str(e)}"}

async def download_and_resize_image(image_url: str, base_url: str = None) -> str:
    try:
        # Handle relative paths
        if image_url.startswith('/') and base_url:
            image_url = f"{base_url.rstrip('/')}{image_url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=10) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    image = image.convert('RGB')
                    max_width = 640
                    if image.width > max_width:
                        ratio = max_width / float(image.width)
                        height = int((float(image.height) * float(ratio)))
                        image = image.resize((max_width, height), Image.LANCZOS)
                    image_hash = hashlib.md5(image_url.encode('utf-8')).hexdigest()
                    image_filename = f"{image_hash}.jpg"
                    image_path = os.path.join(IMAGE_DIR, image_filename)
                    image.save(image_path, "JPEG")
                    return image_filename
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
    return None