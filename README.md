# Yet Another Hacker News Clone

YAHNC is a FastAPI-based web application that fetches and displays top stories from Hacker News with additional features like trend indicators when a story is trending and images fetched from Open Graph metadata.

## Features

- Fetches top 30 stories from Hacker News API
- Displays stories with images, descriptions, and metadata
- Shows trending information for trending stories
- Dark mode toggle
- Responsive design using Tailwind CSS
- Automatic page refresh every 15 minutes

## Tech Stack

- Backend: Python 3.10+, FastAPI, SQLAlchemy, aiohttp
- Frontend: HTML, Tailwind CSS, JavaScript
- Database: SQLite (with aiosqlite for async operations)
- Other: BeautifulSoup4, Pillow

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/hn-clone.git
   cd hn-clone
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   uvicorn main:app --reload
   ```

5. Open your browser and navigate to `http://localhost:8000`

## Project Structure

- `main.py`: FastAPI application and main route
- `hn_scraper.py`: Hacker News API scraper
- `database.py`: Database operations and ORM setup
- `metadata.py`: Metadata fetching and image processing
- `models.py`: SQLAlchemy models
- `templates/`: HTML templates
- `static/`: Static files (CSS, images)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
