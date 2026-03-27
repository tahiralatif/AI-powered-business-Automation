"""
AI Co-founder SaaS Backend - Multi-User Startup Architecture
FastAPI application with database, Slack OAuth, and SendGrid integration
"""
import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from dotenv import load_dotenv

import bcrypt
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import init_db, get_db, get_db_session
from models import User, Settings, ResearchReport, CompetitorChange
from integrations.sendgrid_email import sendgrid_service
from integrations.slack_oauth import slack_oauth_service
from integrations.slack_notifier import send_slack_alert

# Agent imports
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, AsyncOpenAI, Runner, ModelSettings
from agents import RunContextWrapper, TResponseInputItem, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from agent_hooks import AgentBasedHooks
from tools.tools import web_search
from tools.gnews_tool import search_news
from tools.arxiv import search_arxiv
from tools.reddit import get_reddit_trending
from tools.x_com import search_tweets
from tools.finance_tool import finance_tool
from tools.swot_tool import swot_tool
from tools.market_research_tool import market_research_tool
from handoffagents.bussiness_plan_agen import agent as business_plan_agent
from handoffagents.competitorWebsiteScraper import competitorWebsiteScrapert
from handoffagents.pitch_deck_agent import pitch_deck_agent
from handoffagents.idea_generator import idea_generator_agent
from guadrails.input_guardrail import input_guard_agent
from guadrails.output_guardrails import out_guard_agent
from workflow_manager import validate_idea_workflow
from tasks import weekly_research_task, daily_competitor_check_task

load_dotenv()

# FastAPI App
app = FastAPI(
    title="AI Co-founder Automation Engine",
    description="Multi-user startup architecture with Slack OAuth and SendGrid",
    version="2.0.0"
)

# Security
security = HTTPBearer(auto_error=False)


# ==================== Pydantic Models ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SettingsUpdate(BaseModel):
    industry: Optional[str] = None
    competitors: Optional[List[str]] = None
    report_language: Optional[str] = None
    monitoring_enabled: Optional[bool] = None
    daily_digest_enabled: Optional[bool] = None
    weekly_report_enabled: Optional[bool] = None

class IdeaValidationRequest(BaseModel):
    idea: str
    industry: Optional[str] = None

class SlackInstallResponse(BaseModel):
    success: bool
    message: str
    authorization_url: Optional[str] = None


# ==================== Helper Functions ====================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token.
    For now, uses simple email-based auth (implement JWT in production).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Simple token-based auth (replace with JWT in production)
    token = credentials.credentials
    user = db.query(User).filter(User.email == token).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return user


def get_or_create_settings(db: Session, user: User) -> Settings:
    """Get user settings or create default settings."""
    settings = db.query(Settings).filter(Settings.user_id == user.id).first()
    
    if not settings:
        settings = Settings(
            user_id=user.id,
            industry="AI SaaS",
            competitors=[],
            report_language="english",
            monitoring_enabled=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


# ==================== Public Endpoints ====================

@app.get("/")
async def root():
    return {
        "status": "AI Co-founder Automation Engine is running",
        "version": "2.0.0 - Multi-User Architecture",
        "features": ["Database", "Slack OAuth", "SendGrid Email"]
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ==================== Authentication Endpoints ====================

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    Sends welcome email via SendGrid.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password (using simple hash for demo, use bcrypt in production)
    from passlib.hash import bcrypt
    hashed_password = bcrypt.hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default settings
    settings = Settings(user_id=user.id)
    db.add(settings)
    db.commit()
    
    # Send welcome email
    try:
        sendgrid_service.send_welcome_email(user.email, user.full_name)
    except Exception as e:
        print(f"Warning: Could not send welcome email: {e}")
    
    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email
    }


@app.post("/auth/login")
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get access token.
    For simplicity, returns email as token (implement JWT in production).
    """
    from passlib.hash import bcrypt
    
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not bcrypt.verify(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Return simple token (replace with JWT in production)
    return {
        "access_token": user.email,  # Simple token for demo
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }


# ==================== User Settings Endpoints ====================

@app.get("/users/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile and settings."""
    settings = get_or_create_settings(db, current_user)
    
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at
        },
        "settings": {
            "industry": settings.industry,
            "competitors": settings.competitors,
            "report_language": settings.report_language,
            "monitoring_enabled": settings.monitoring_enabled,
            "slack_installed": settings.slack_installed,
            "slack_team_name": settings.slack_team_name
        }
    }


@app.put("/users/me/settings")
async def update_user_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user settings."""
    settings = get_or_create_settings(db, current_user)
    
    update_data = settings_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return {"message": "Settings updated successfully", "settings": settings}


@app.get("/users/me/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user settings."""
    settings = get_or_create_settings(db, current_user)
    return settings


# ==================== Slack OAuth Endpoints ====================

@app.get("/slack/install")
async def slack_install(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate Slack OAuth flow.
    Redirect user to Slack authorization page.
    """
    state = f"user_{current_user.id}"
    auth_url = slack_oauth_service.get_authorization_url(state)
    
    return {
        "success": True,
        "message": "Redirect to Slack for authorization",
        "authorization_url": auth_url
    }


@app.get("/slack/callback")
async def slack_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Slack OAuth callback.
    Exchange code for token and save to database.
    """
    if error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Slack authorization failed: {error}"}
        )
    
    if not code:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "No authorization code received"}
        )
    
    try:
        # Exchange code for token
        token_data = await slack_oauth_service.exchange_code_for_token(code)
        
        # Extract user_id from state (format: "user_123")
        user_id = None
        if state and state.startswith("user_"):
            user_id = int(state.split("_")[1])
        
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid state parameter"}
            )
        
        # Get user and settings
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "User not found"}
            )
        
        settings = get_or_create_settings(db, user)
        
        # Save Slack credentials
        settings.slack_access_token = token_data["access_token"]
        settings.slack_team_id = token_data["team_id"]
        settings.slack_team_name = token_data["team_name"]
        settings.slack_user_id = token_data["user_id"]
        settings.slack_installed = True
        settings.slack_installed_at = datetime.utcnow()
        
        # Create private channel
        try:
            channel_data = await slack_oauth_service.find_or_create_channel(
                token_data["access_token"],
                "ai-cofounder-insights"
            )
            settings.slack_channel_id = channel_data["channel_id"]
        except Exception as e:
            print(f"Warning: Could not create channel: {e}")
        
        db.commit()
        
        # Send success notification
        await slack_oauth_service.send_message(
            token_data["access_token"],
            settings.slack_channel_id,
            "🎉 *AI Co-founder installed successfully!*\n\nYou'll now receive automated business insights and competitor alerts in this channel."
        )
        
        return RedirectResponse(url="/slack/success?team=" + str(token_data["team_name"] or "Slack"))
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


@app.get("/slack/success")
async def slack_success(team: str = "your workspace"):
    """Slack installation success page."""
    return {
        "success": True,
        "message": f"AI Co-founder has been installed to {team}!",
        "next_steps": [
            "Check your #ai-cofounder-insights channel",
            "Configure your industry and competitors in settings",
            "Enable automated reports"
        ]
    }


@app.post("/slack/disconnect")
async def slack_disconnect(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Slack integration."""
    settings = get_or_create_settings(db, current_user)
    
    # Revoke token (optional)
    if settings.slack_access_token:
        try:
            requests.post(
                "https://slack.com/api/auth.revoke",
                headers={"Authorization": f"Bearer {settings.slack_access_token}"}
            )
        except Exception as e:
            print(f"Warning: Could not revoke token: {e}")
    
    # Clear stored data
    settings.slack_access_token = None
    settings.slack_team_id = None
    settings.slack_team_name = None
    settings.slack_user_id = None
    settings.slack_channel_id = None
    settings.slack_installed = False
    settings.slack_installed_at = None
    
    db.commit()
    
    return {"message": "Slack integration disconnected successfully"}


@app.get("/slack/status")
async def slack_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check Slack integration status."""
    settings = get_or_create_settings(db, current_user)
    
    if not settings.slack_installed or not settings.slack_access_token:
        return {"installed": False, "message": "Slack not connected"}
    
    # Verify token is still valid
    is_valid = slack_oauth_service.verify_token(settings.slack_access_token)
    
    return {
        "installed": settings.slack_installed,
        "team_name": settings.slack_team_name,
        "team_id": settings.slack_team_id,
        "channel_id": settings.slack_channel_id,
        "token_valid": is_valid,
        "installed_at": settings.slack_installed_at
    }


# ==================== Schedule Endpoints ====================

@app.get("/schedule/status")
async def schedule_status():
    """Returns the status of scheduled tasks."""
    return {
        "tasks": [
            {"name": "Weekly Market Research", "schedule": "Every Monday at 9 AM"},
            {"name": "Daily Competitor Check", "schedule": "Every Night at 11 PM"},
            {"name": "Monthly Digest", "schedule": "1st of every Month"}
        ],
        "system": "Celery + Redis"
    }


@app.post("/schedule/run-now/{task_name}")
async def run_task_immediately(
    task_name: str,
    current_user: User = Depends(get_current_user)
):
    """Manually triggers a task without waiting for the schedule."""
    if task_name == "weekly-research":
        weekly_research_task.delay()
        return {"msg": "Weekly research task triggered in background."}
    elif task_name == "competitor-check":
        daily_competitor_check_task.delay()
        return {"msg": "Competitor check task triggered in background."}
    else:
        return {"error": "Unknown task name."}


# ==================== Idea Validation Endpoint ====================

@app.post("/validate-idea")
async def validate_idea(
    request: IdeaValidationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate a business idea using AI agents."""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.0-flash"

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY not configured"
        )

    client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    Gemini_model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )

    config = RunConfig(
        model=Gemini_model,
        model_provider=client,
        tracing_disabled=True
    )

    @input_guardrail
    async def guardrail_input_func(
        ctx: RunContextWrapper[None],
        agent: Agent,
        input: str | list[TResponseInputItem],
    ) -> GuardrailFunctionOutput:
        result = await Runner.run(
            input_guard_agent,
            input=input,
            context=ctx.context,
            run_config=config
        )

        return GuardrailFunctionOutput(
            output_info=result.final_output,
            tripwire_triggered=not result.final_output.is_business_or_startup_idea_competitor_pitch_related,
        )

    @output_guardrail
    async def guardrail_output_func(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | list[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(
                out_guard_agent,
                input=input,
                context=ctx.context,
                run_config=config
            )

            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=not result.final_output.is_business_or_startup_idea_competitor_pitch_related,
            )

    triage_agent = Agent(
        name="Orchestrator Agent",
        instructions="""
        You are the Orchestrator Agent.
        Your job is to analyze the user's request and ALWAYS hand it off to the most suitable specialized agent.
        You must not solve tasks directly yourself — only route them to the right agent.
        """,
        tools=[
            business_plan_agent.as_tool(
                tool_name="business_plan_agent",
                tool_description="Creates structured, investor-ready business plans."
            ),
            idea_generator_agent.as_tool(
                tool_name="idea_generator_agent",
                tool_description="Generates unique, practical, and creative ideas based on user prompts."
            ),
            competitorWebsiteScrapert.as_tool(
                tool_name="competitor_website_scraper_agent",
                tool_description="Scrapes competitor websites to gather insights and data for market analysis."
            ),
            pitch_deck_agent.as_tool(
                tool_name="pitch_deck_generator_agent",
                tool_description="Generates a full 10-slide pitch deck draft."
            )
        ],
        hooks=AgentBasedHooks(),
        model_settings=ModelSettings(
            tool_choice="required",
            max_tokens=600,
            temperature=0.9,
            top_p=0.9,
        ),
        handoffs=[business_plan_agent, idea_generator_agent, competitorWebsiteScrapert, pitch_deck_agent],
        handoff_description="""
        The Orchestrator Agent MUST select one of the following agents for every request:
        - Business Plan Agent → For structured, investor-ready business plans.
        - Idea Generator Agent → For unique, practical, and creative ideas.
        - Competitor Website Scraper Agent → For scraping and analyzing competitor websites.
        - Pitch Deck Generator Agent → For professional 10-slide pitch deck drafts.
        """,
        input_guardrails=[guardrail_input_func],
        output_guardrails=[guardrail_output_func]
    )

    try:
        result_workflow = await validate_idea_workflow(request.idea)
        
        # Save report to database
        report = ResearchReport(
            user_id=current_user.id,
            report_type="validation",
            title=f"Idea Validation: {request.idea[:50]}...",
            summary=result_workflow[:500] if isinstance(result_workflow, str) else "Validation complete",
            content={"idea": request.idea, "result": result_workflow},
            is_sent=False
        )
        db.add(report)
        db.commit()
        
        return {
            "success": True,
            "validation_result": result_workflow,
            "report_id": report.id
        }

    except InputGuardrailTripwireTriggered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Input must be related to business or startup ideas"
        )

    except OutputGuardrailTripwireTriggered:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generated output validation failed"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Startup ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("🚀 AI Co-founder SaaS started with multi-user architecture!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
