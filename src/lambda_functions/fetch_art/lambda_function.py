import json
import urllib.request
import urllib.error
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def fetch_artworks_from_api():
    """Fetch artworks from Art Institute of Chicago API"""
    base_url = "https://api.artic.edu/api/v1/artworks"
    params = {"limit": 9, "fields": "id,title,artist_display,date_display,image_id"}

    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    url = f"{base_url}?{query_string}"

    try:
        request = urllib.request.Request(url)
        request.add_header("User-Agent", "CloudGallery/1.0")

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])

    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error {e.code}: {e.reason}")
        raise
    except urllib.error.URLError as e:
        logger.error(f"URL error: {e.reason}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise


def process_artwork_data(artworks):
    """Clean and format artwork data"""
    processed = []
    current_time = datetime.utcnow().isoformat()

    for artwork in artworks:
        if not artwork.get("id") or not artwork.get("title"):
            continue

        processed_artwork = {
            "artwork_id": str(artwork["id"]),
            "title": artwork.get("title", "Untitled").strip(),
            "artist": artwork.get("artist_display", "Unknown Artist").strip(),
            "date": artwork.get("date_display", "Unknown Date").strip(),
            "image_id": artwork.get("image_id"),
            "fetched_at": current_time,
        }
        processed.append(processed_artwork)

    return processed


def lambda_handler(event, context):
    logger.info("Starting artwork fetch process")

    try:
        raw_artworks = fetch_artworks_from_api()
        logger.info(f"Fetched {len(raw_artworks)} raw artworks")

        processed_artworks = process_artwork_data(raw_artworks)
        logger.info(f"Processed {len(processed_artworks)} valid artworks")

        return {
            "statusCode": 200,
            "body": {
                "artworks": processed_artworks,
                "count": len(processed_artworks),
                "message": "Successfully fetched artworks",
            },
        }

    except Exception as e:
        logger.error(f"Error fetching artworks: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"artworks": [], "count": 0, "error": str(e)},
        }
