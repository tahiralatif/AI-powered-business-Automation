# AI Co-founder SaaS - Startup Architecture Setup Guide

## 🎯 Overview

This is a **production-ready, multi-user startup architecture** for the AI Co-founder platform. It includes:

1. **Database (SQLAlchemy + SQLite/PostgreSQL)** - Multi-user support with proper authentication
2. **SendGrid Integration** - Professional email delivery (100 emails/day free)
3. **Slack OAuth** - "Add to Slack" button for seamless workspace integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database (SQLite for development)
DATABASE_URL=sqlite:///./ai_cofounder.db

# SendGrid Email (Get API key from https://sendgrid.com/)
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=AI Co-founder Automation

# Slack OAuth (Create app at https://api.slack.com/apps)
SLACK_CLIENT_ID=your_slack_client_id_here
SLACK_CLIENT_SECRET=your_slack_client_secret_here
SLACK_REDIRECT_URI=http://localhost:8000/slack/callback
SLACK_SCOPES=channels:manage,channels:read,chat:write,chat:write.public,im:write,groups:read

# AI & Search
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Migration

Migrate existing `config.json` data to the database:

```bash
.venv\Scripts\python.exe migrate_config_to_db.py
```

**Default credentials after migration:**
- Email: `tahira@example.com`
- Password: `changeme123`

### 4. Start the Server

```bash
.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
backend/
├── main.py                    # FastAPI application with all endpoints
├── models.py                  # SQLAlchemy database models
├── database.py                # Database connection and session management
├── migrate_config_to_db.py    # Migration script from config.json
├── tasks.py                   # Celery tasks for scheduled jobs
├── integrations/
│   ├── sendgrid_email.py      # SendGrid email service
│   ├── slack_oauth.py         # Slack OAuth 2.0 flow
│   └── slack_notifier.py      # Legacy Slack webhook notifier
└── config.json                # (Legacy - now in database)
```

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get access token |

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| GET | `/users/me/settings` | Get user settings |
| PUT | `/users/me/settings` | Update user settings |

### Slack Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/slack/install` | Initiate Slack OAuth flow |
| GET | `/slack/callback` | OAuth callback handler |
| GET | `/slack/status` | Check Slack connection status |
| POST | `/slack/disconnect` | Disconnect Slack integration |

### Task Scheduling

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/schedule/status` | Get scheduled tasks status |
| POST | `/schedule/run-now/{task_name}` | Trigger task immediately |

### Idea Validation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/validate-idea` | Validate business idea with AI |

## 📖 Usage Examples

### 1. Register New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "user@example.com",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com"
}
```

### 3. Add to Slack (Frontend Button)

On your frontend dashboard, create a button:

```html
<a href="http://localhost:8000/slack/install" class="btn-slack">
  <img src="https://platform.slack-edge.com/img/add_to_slack.png" alt="Add to Slack">
</a>
```

When user clicks:
1. Redirects to Slack authorization
2. User approves permissions
3. Callback saves token to database
4. Private channel `#ai-cofounder-insights` is created
5. Success page shown

### 4. Update User Settings

```bash
curl -X PUT http://localhost:8000/users/me/settings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer user@example.com" \
  -d '{
    "industry": "E-commerce",
    "competitors": ["https://shopify.com", "https://woocommerce.com"],
    "monitoring_enabled": true
  }'
```

### 5. Validate Business Idea

```bash
curl -X POST http://localhost:8000/validate-idea \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer user@example.com" \
  -d '{
    "idea": "A subscription box for eco-friendly office supplies"
  }'
```

## 🗄️ Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String | Unique user email |
| hashed_password | String | Bcrypt hashed password |
| full_name | String | User's full name |
| is_active | Boolean | Account status |
| created_at | DateTime | Registration date |

### Settings Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to Users |
| industry | String | User's industry |
| competitors | JSON | List of competitor URLs |
| slack_access_token | String | Slack OAuth token |
| slack_installed | Boolean | Slack integration status |
| monitoring_enabled | Boolean | Enable automated tasks |

## 📧 SendGrid Setup

1. **Create Account**: Go to [SendGrid](https://sendgrid.com/)
2. **Verify Domain**: Add your domain for professional emails
3. **Get API Key**: Settings → API Keys → Create API Key
4. **Add to .env**:
   ```
   SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
   SENDGRID_FROM_EMAIL=noreply@yourdomain.com
   ```

**Free Tier**: 100 emails/day (perfect for startups!)

## 💬 Slack App Setup

1. **Create App**: Go to [Slack API Apps](https://api.slack.com/apps)
2. **Add Redirect URL**: `http://localhost:8000/slack/callback`
3. **OAuth & Permissions**:
   - Add scopes: `channels:manage`, `channels:read`, `chat:write`, `im:write`
   - Install to workspace
4. **Get Credentials**:
   - Client ID
   - Client Secret
5. **Add to .env**:
   ```
   SLACK_CLIENT_ID=1234567890.1234567890
   SLACK_CLIENT_SECRET=abcdef1234567890
   ```

## 🔄 Migration from config.json

The migration script automatically:
- Creates user from `config.json` email
- Imports industry and competitors
- Preserves monitoring settings
- Creates default password

**After migration**, `config.json` is no longer used. All data is in the database.

## 🛡️ Security Notes

### Current Implementation (Development)
- Simple email-based authentication
- Bcrypt password hashing
- Basic token (email) for API access

### Production Recommendations
1. **JWT Tokens**: Implement proper JWT authentication
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Email Verification**: Verify user emails on registration
5. **Password Reset**: Implement password reset flow
6. **2FA**: Add two-factor authentication

## 📊 Scaling Considerations

### Database
- **Development**: SQLite (file-based, simple)
- **Production**: PostgreSQL (robust, scalable)

Change in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_cofounder_db
```

### Email
- **Current**: SendGrid (100/day free)
- **Upgrade**: SendGrid Pro ($19.95/month for 40k emails)

### Task Queue
- **Current**: Celery + Redis
- **Scale**: Multiple Celery workers, Redis cluster

## 🧪 Testing

### Test User Registration
```bash
curl http://localhost:8000/health
```

### Test Database Connection
```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer tahira@example.com"
```

## 📝 Next Steps

1. **Frontend Integration**: Connect React/Vue dashboard to these APIs
2. **Payment Gateway**: Add Stripe for subscriptions
3. **Analytics**: Add Mixpanel/Amplitude for user tracking
4. **Monitoring**: Set up Sentry for error tracking
5. **CI/CD**: Configure GitHub Actions for deployment

## 🤝 Support

For issues or questions:
- Check the code comments
- Review the API endpoint documentation
- Test with curl commands first

---

**Built with ❤️ for startups** - Scalable from day one!
