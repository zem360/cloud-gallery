import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")


def get_table_name():
    import os

    table_name = os.environ.get("DYNAMODB_TABLE_NAME")
    if not table_name:
        raise ValueError("DYNAMODB_TABLE_NAME environment variable not set")
    return table_name


def prepare_item_for_dynamodb(artwork, date_fetched):
    item = {
        "artwork_id": artwork["artwork_id"],
        "date_fetched": date_fetched,
        "title": artwork["title"],
        "artist": artwork["artist"],
        "date_display": artwork["date"],
        "fetched_at": artwork["fetched_at"],
        "status": "active",
    }

    if artwork.get("image_id"):
        item["image_id"] = artwork["image_id"]

    return item


def store_artworks_in_dynamodb(artworks):
    table_name = get_table_name()
    table = dynamodb.Table(table_name)

    date_fetched = datetime.utcnow().strftime("%Y-%m-%d")
    stored_count = 0
    errors = []

    logger.info(f"Storing {len(artworks)} artworks in table: {table_name}")

    for artwork in artworks:
        try:
            item = prepare_item_for_dynamodb(artwork, date_fetched)

            table.put_item(Item=item)
            stored_count += 1

            logger.debug(f"Stored artwork: {artwork['artwork_id']}")

        except ClientError as e:
            error_msg = f"Failed to store artwork {artwork['artwork_id']}: {e.response['Error']['Message']}"
            logger.error(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = (
                f"Unexpected error storing artwork {artwork['artwork_id']}: {str(e)}"
            )
            logger.error(error_msg)
            errors.append(error_msg)

    return stored_count, errors


def lambda_handler(event, context):
    logger.info("Starting artwork processing and storage")

    try:
        if "body" in event and "artworks" in event["body"]:
            artworks = event["body"]["artworks"]
        else:
            raise ValueError("No artworks found in event data")

        logger.info(f"Processing {len(artworks)} artworks")

        if not artworks:
            return {
                "statusCode": 200,
                "body": {
                    "stored_count": 0,
                    "message": "No artworks to process",
                    "errors": [],
                },
            }

        stored_count, errors = store_artworks_in_dynamodb(artworks)

        if stored_count == 0:
            status_code = 500
            message = "Failed to store any artworks"
        elif errors:
            status_code = 207  # Partial success
            message = f"Stored {stored_count} artworks with {len(errors)} errors"
        else:
            status_code = 200
            message = f"Successfully stored {stored_count} artworks"

        logger.info(message)

        return {
            "statusCode": status_code,
            "body": {
                "stored_count": stored_count,
                "total_artworks": len(artworks),
                "message": message,
                "errors": errors[:5],  # Limit error details
                "artworks": artworks,  # Pass through for next step
            },
        }

    except Exception as e:
        logger.error(f"Error processing artworks: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"stored_count": 0, "error": str(e), "artworks": []},
        }
