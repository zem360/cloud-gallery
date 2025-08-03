import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_pipeline_completion(artworks_count, website_url):
    completion_time = datetime.utcnow().isoformat()

    logger.info("=== CLOUD GALLERY PIPELINE COMPLETED ===")
    logger.info(f"Completion Time: {completion_time}")
    logger.info(f"Artworks Processed: {artworks_count}")
    logger.info(f"Website URL: {website_url}")
    logger.info("Status: SUCCESS")
    logger.info("==========================================")


def generate_completion_summary(event):
    try:
        body = event.get("body", {})
        artworks_count = body.get("artworks_count", 0)
        website_url = body.get("url", "Unknown")

        summary = {
            "pipeline_status": "SUCCESS",
            "execution_time": datetime.utcnow().isoformat(),
            "artworks_processed": artworks_count,
            "website_url": website_url,
            "steps_completed": [
                "Fetched artworks from Art Institute API",
                "Stored artwork data in DynamoDB",
                "Generated interactive HTML gallery",
                "Uploaded gallery to S3 website",
            ],
        }

        return summary

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {
            "pipeline_status": "ERROR",
            "execution_time": datetime.utcnow().isoformat(),
            "error": str(e),
        }


def send_completion_notification(summary):
    # Future enhancement: Send email or SNS notification
    # For now, just log the notification

    status = summary.get("pipeline_status", "UNKNOWN")
    artworks_count = summary.get("artworks_processed", 0)
    website_url = summary.get("website_url", "Unknown")

    notification_message = f"""
    🎨 Cloud Gallery Daily Update Complete!
    
    Status: {status}
    Artworks: {artworks_count} new pieces added
    Gallery: {website_url}
    
    Your daily art collection is ready to view!
    """

    logger.info(f"NOTIFICATION: {notification_message}")

    # Placeholder for actual notification service

    return {"notification_sent": True, "message": notification_message.strip()}


def lambda_handler(event, context):
    logger.info("Starting pipeline completion and notifications")

    try:
        summary = generate_completion_summary(event)

        if summary.get("pipeline_status") == "SUCCESS":
            log_pipeline_completion(
                summary.get("artworks_processed", 0),
                summary.get("website_url", "Unknown"),
            )

        notification_result = send_completion_notification(summary)

        response = {
            "statusCode": 200,
            "body": {
                "message": "Pipeline completed successfully",
                "summary": summary,
                "notification": notification_result,
                "final_status": "COMPLETE",
            },
        }

        logger.info("Pipeline completion process finished successfully")
        return response

    except Exception as e:
        logger.error(f"Error in completion process: {str(e)}")
        return {
            "statusCode": 500,
            "body": {
                "message": "Pipeline completion failed",
                "error": str(e),
                "final_status": "ERROR",
            },
        }
