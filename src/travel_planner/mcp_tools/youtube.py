"""MCP-style tool wrapper around the YouTube Data API for short-video search."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"


def search_short_videos(query: str, max_results: int = 4) -> list[dict]:
	"""Tool: search_short_videos - find short YouTube videos matching a query.

	Returns [] if YOUTUBE_API_KEY is not configured or the request fails, so
	callers can fall back to a static alternative.
	"""
	if not YOUTUBE_API_KEY:
		return []

	try:
		response = httpx.get(
			f"{YOUTUBE_BASE_URL}/search",
			params={
				"part": "snippet",
				"q": query,
				"type": "video",
				"videoDuration": "short",
				"order": "viewCount",
				"maxResults": max_results,
				"key": YOUTUBE_API_KEY,
			},
			timeout=10.0,
		)
		response.raise_for_status()
	except httpx.HTTPError as e:
		print(f"youtube: search failed for {query!r}: {e}")
		return []

	items = response.json().get("items", [])
	return [
		{"id": item["id"]["videoId"], "title": item["snippet"]["title"]}
		for item in items
		if item.get("id", {}).get("videoId")
	]
