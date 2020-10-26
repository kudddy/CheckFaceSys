from aiohttp.web import run_app
from app import create_app

app = create_app()
run_app(app)
