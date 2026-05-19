import logging
import requests
from backend.core.config import settings

logger = logging.getLogger(__name__)

class SlackService:
    def send_webhook_alert(self, title: str, text: str, status: str = "info") -> bool:
        """Sends a notification to a Slack channel via incoming webhooks."""
        if not settings.SLACK_WEBHOOK_URL:
            logger.info(f"[Slack Webhook Mock Alert] Title: {title} | Status: {status} | Text: {text}")
            return True

        color = "#8a2be2"  # Purple
        if status == "success":
            color = "#00ff7f"  # Green
        elif status == "failed" or status == "error":
            color = "#ff453a"  # Red

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"AI Bug Reproduction System: {title}",
                    "text": text,
                    "fallback": f"{title} - {text}"
                }
            ]
        }

        try:
            response = requests.post(settings.SLACK_WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code == 200:
                return True
            logger.warning(f"Slack Webhook returned status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send Slack Webhook alert: {e}")
            
        return False

    def post_message(self, channel: str, text: str, thread_ts: str = None) -> bool:
        """Posts a message back to Slack channel using Web Client API (bot token)."""
        if not settings.SLACK_BOT_TOKEN:
            logger.info(f"[Slack Chat Bot Mock Message] Channel: {channel} | Thread: {thread_ts} | Text: {text}")
            return True

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel,
            "text": text
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            data = response.json()
            if data.get("ok"):
                return True
            logger.warning(f"Slack postMessage failed: {data.get('error')}")
        except Exception as e:
            logger.error(f"Failed to post Slack message: {e}")
            
        return False

slack_service = SlackService()
