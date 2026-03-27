"""
Slack OAuth Service
Handles "Add to Slack" button flow and token management
"""
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
import httpx

load_dotenv()


class SlackOAuthService:
    """
    Handles Slack OAuth 2.0 flow for workspace installation.
    
    Flow:
    1. User clicks "Add to Slack" button
    2. Redirect to Slack authorization URL
    3. User approves in Slack
    4. Callback with authorization code
    5. Exchange code for access token
    6. Store token in database
    """

    def __init__(self):
        self.client_id = os.getenv("SLACK_CLIENT_ID")
        self.client_secret = os.getenv("SLACK_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SLACK_REDIRECT_URI", "http://localhost:8000/slack/callback")
        self.scopes = os.getenv(
            "SLACK_SCOPES",
            "channels:manage,channels:read,chat:write,chat:write.public,im:write,groups:read"
        )

        if not self.client_id or not self.client_secret:
            print("⚠️ Slack OAuth credentials not configured. Check SLACK_CLIENT_ID and SLACK_CLIENT_SECRET in .env")

    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate the Slack authorization URL for the "Add to Slack" button.

        Args:
            state: Optional state parameter for CSRF protection (recommended: user_id or session token)

        Returns:
            str: Slack authorization URL
        """
        if not self.client_id:
            raise ValueError("SLACK_CLIENT_ID not configured")

        # Build authorization URL manually for better control
        base_url = "https://slack.com/oauth/v2/authorize"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state or "ai_cofounder_install"
        }

        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from Slack callback

        Returns:
            dict: Token response containing access_token, team info, etc.
        """
        if not self.client_secret:
            raise ValueError("SLACK_CLIENT_SECRET not configured")

        token_url = "https://slack.com/api/oauth.v2.access"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                token_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri
                }
            )

            result = response.json()

            if not result.get("ok"):
                raise ValueError(f"Slack OAuth error: {result.get('error', 'Unknown error')}")

            return {
                "access_token": result.get("access_token"),
                "team_id": result.get("team", {}).get("id"),
                "team_name": result.get("team", {}).get("name"),
                "user_id": result.get("authed_user", {}).get("id"),
                "scope": result.get("scope"),
                "bot_user_id": result.get("bot_user_id"),
                "app_id": result.get("app_id")
            }

    async def create_private_channel(self, access_token: str, channel_name: str = "ai-cofounder-insights") -> dict:
        """
        Create a private channel for AI Co-founder insights.

        Args:
            access_token: Slack access token
            channel_name: Name for the private channel

        Returns:
            dict: Channel information including channel_id
        """
        url = "https://slack.com/api/conversations.create"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "name": channel_name,
            "is_private": True
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            result = response.json()

            if not result.get("ok"):
                # Channel might already exist, try to find it
                if "channel_already_exists" in result.get("error", ""):
                    return await self.find_or_create_channel(access_token, channel_name)
                raise ValueError(f"Slack API error: {result.get('error', 'Unknown error')}")

            return {
                "channel_id": result.get("channel", {}).get("id"),
                "channel_name": channel_name
            }

    async def find_or_create_channel(self, access_token: str, channel_name: str) -> dict:
        """
        Find existing channel or create a new one.

        Args:
            access_token: Slack access token
            channel_name: Name of the channel to find

        Returns:
            dict: Channel information
        """
        # List all private channels
        url = "https://slack.com/api/conversations.list"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"types": "private_channel", "limit": 100}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            result = response.json()

            if result.get("ok"):
                channels = result.get("channels", [])
                for channel in channels:
                    if channel.get("name") == channel_name:
                        return {
                            "channel_id": channel.get("id"),
                            "channel_name": channel_name,
                            "existing": True
                        }

            # If not found, create new channel
            return await self.create_private_channel(access_token, channel_name)

    async def send_message(self, access_token: str, channel_id: str, message: str, blocks: list = None) -> bool:
        """
        Send a message to a Slack channel.

        Args:
            access_token: Slack access token
            channel_id: Target channel ID
            message: Message text
            blocks: Optional rich formatting blocks

        Returns:
            bool: Success status
        """
        url = "https://slack.com/api/chat.postMessage"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {
            "channel": channel_id,
            "text": message
        }
        if blocks:
            data["blocks"] = blocks

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            result = response.json()

            if not result.get("ok"):
                print(f"❌ Slack message error: {result.get('error')}")
                return False

            return True

    def verify_token(self, access_token: str) -> bool:
        """
        Verify if a Slack access token is valid.

        Args:
            access_token: Token to verify

        Returns:
            bool: True if valid
        """
        url = "https://slack.com/api/auth.test"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.post(url, headers=headers)
            result = response.json()
            return result.get("ok", False)
        except Exception as e:
            print(f"❌ Token verification error: {e}")
            return False


# Singleton instance
slack_oauth_service = SlackOAuthService()
