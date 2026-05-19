import logging
from fastapi import APIRouter, Request, HTTPException
from backend.services.slack_service import slack_service
from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/events")
async def slack_events(request: Request):
    """
    Slack Event subscription endpoint.
    Handles URL verification challenges and incoming event messages.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    # 1. Handle Slack Challenge Verification
    if body.get("type") == "url_verification":
        challenge = body.get("challenge")
        if not challenge:
            raise HTTPException(status_code=400, detail="Challenge parameter missing")
        return {"challenge": challenge}

    # 2. Process events asynchronously or inline for quick responder.
    # Slack expects 200 OK within 3 seconds, so we process incoming mentions/messages.
    event = body.get("event", {})
    event_type = event.get("type")

    # Handle bot mentions or direct messages
    if event_type in ["app_mention", "message"]:
        # Avoid responding to bot's own messages
        if event.get("bot_id") or event.get("user") == body.get("authorizations", [{}])[0].get("user_id"):
            return {"status": "ignored"}

        channel = event.get("channel")
        text = event.get("text", "")
        thread_ts = event.get("thread_ts") or event.get("ts")

        # Strip mention handle if it's an app_mention (e.g. <@U123456>)
        cleaned_text = text
        if event_type == "app_mention":
            import re
            cleaned_text = re.sub(r"<@\w+>\s*", "", text).strip()

        # Query AI to get response
        system_prompt = "You are the AI Bug Reproduction Assistant inside a Slack channel. Keep answers direct, brief and clear."
        ai_response = ai_service.generate_response(
            [{"role": "user", "content": cleaned_text}],
            system_prompt=system_prompt
        )

        # Post response back to Slack
        slack_service.post_message(
            channel=channel,
            text=ai_response,
            thread_ts=thread_ts
        )

    return {"status": "ok"}
