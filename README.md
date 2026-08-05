# AI Content OS

**Unified AI-Powered Content Operating System**

Integrates Pinterest AI Studio, Multi-Agent System, Graphic Rendering Engine, and Website CMS into one modular platform.

## Architecture

```
apps/
  api/          # FastAPI backend — unified API with 15+ modules
  dashboard/    # Next.js 15 dashboard — 18 pages, unified navigation

packages/
  ai-core/          # AI provider abstraction (Claude, Gemini)
  trend-engine/     # Trend discovery and analysis
  seo-engine/       # Keyword research and SEO optimization
  content-engine/   # Content generation and optimization
  graphic_engine/   # Code-based graphic rendering engine (17 templates)
  image-engine/     # Image generation abstraction
  analytics-engine/ # Performance analytics
  scheduler/        # Content scheduling
  pinterest/        # Pinterest API integration
  database/         # Database utilities
  auth/             # Authentication
  notifications/    # Notification system
```

## Master Workflow

```
1. User enters a topic
2. Trend Agent researches opportunities
3. SEO Agent builds keyword clusters
4. Content Agent generates article draft
5. Graphic Rendering Engine creates Pinterest graphics
6. Pinterest module generates titles, descriptions, hashtags
7. Everything stored as draft in Website CMS
8. User reviews and edits content
9. User approves publication
10. Article published to website
11. Pinterest assets added to publishing queue
12. Analytics begin tracking performance
13. Revenue Dashboard reports earnings
```

## Database (19 tables)

Users, Articles, Categories, Tags, Pins, Boards, Keywords, Media, Graphics, Analytics, Schedules, Images, Settings, Logs, AffiliateLinks, AIJobs, PublishingQueue, Notifications, Revenue

## Dashboard Pages (18 total)

| Page | Description |
|------|-------------|
| Overview | Central dashboard with stats, agent status, activity |
| AI Command Center | 9-agent orchestration with workflow pipeline |
| Content Pipeline | Full pipeline: Research → Generate → Design → Review → Approve → Publish → Track |
| Website CMS | Article management, categories, tags |
| Pinterest Studio | Pinterest-specific graphic studio |
| Graphic Studio | 17-template rendering engine |
| Media Library | Unified assets for website + Pinterest |
| Trend Discovery | Trend scanning with opportunity scores |
| Keyword Research | SEO keyword clusters |
| Content Generator | AI titles, descriptions, hashtags |
| Boards | Board management |
| Publishing Queue | Queue with scheduling |
| Calendar | Content calendar |
| Analytics | Metrics, growth, top content |
| Revenue | Earnings dashboard, affiliate tracking |
| Notifications | AI generation, publishing, analytics alerts |
| AI Insights | Strategy recommendations |
| Settings | AI provider, brand, defaults |

## API Modules (15+)

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | `/auth/*` | Register, login, OAuth, profile |
| Boards | `/boards/*` | Board CRUD |
| Pins | `/pins/*` | Pin CRUD |
| Keywords | `/keywords/*` | Keyword research |
| Analytics | `/analytics/*` | Performance analytics |
| Generator | `/generator/*` | AI content generation |
| Settings | `/settings/*` | User settings |
| Queue | `/queue/*` | Publishing queue |
| Images | `/images/*` | Image uploads |
| Agents | `/agents/*` | Multi-agent orchestration |
| Renderer | `/renderer/*` | Graphic rendering engine |
| CMS | `/articles/*` | Article CRUD |
| CMS | `/cms/*` | Categories & tags |
| Media | `/media/*` | Media library |
| Notifications | `/notifications/*` | Notifications |
| Revenue | `/revenue/*` | Revenue dashboard |

## AI Agents (9)

| Agent | Role |
|-------|------|
| Master | Orchestrates all agents |
| Trend | Discovers trending topics |
| SEO | Keyword clusters, search intent |
| Content | Titles, descriptions, hashtags |
| Design | Image generation, design specs |
| Quality | Grammar, readability, policy |
| Scheduler | Publishing queues, timing |
| Analytics | Performance metrics, reports |
| Strategy | Growth recommendations |

## Quick Start

### Option A — Local (no Docker, recommended for instant dev)

The API defaults to a self-contained SQLite database (`apps/api/pinterest_ai.db`), so no PostgreSQL/Redis/Docker is required.

```bash
# 1. Backend
cd apps/api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # SQLite defaults are already in code — .env is optional
./run_server.sh             # detaches API on http://localhost:8000 (logs: /tmp/pinterest_api.log)

# 2. Dashboard
cd ../dashboard
./run_dashboard.sh          # detaches Next.js on http://localhost:3000 (logs: /tmp/pinterest_dashboard.log)
```

- Dashboard: http://localhost:3000
- API: http://localhost:8000 · Docs: http://localhost:8000/docs
- Stop either server with `pkill -f "uvicorn app.main"` / `pkill -f "next dev"`
- The dashboard auto-provisions a demo account (`demo@example.com`) so every API call is authenticated.

### Option B — Docker Compose (PostgreSQL + Redis)

```bash
cp .env.example .env
docker compose up -d

# Dashboard: http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

## Connecting a real Pinterest account

1. Create a free app at https://developers.pinterest.com (scopes: `boards:read`, `boards:write`, `pins:read`, `pins:write`, `user_accounts:read`)
2. Register the redirect URI `http://localhost:8000/api/v1/pinterest/callback` in the app
3. Add to `apps/api/.env`:
   ```
   PINTEREST_CLIENT_ID=your_client_id
   PINTEREST_CLIENT_SECRET=your_client_secret
   ```
4. Restart the API (`./run_server.sh`) and open **Settings → Pinterest Account** in the dashboard.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Auth | JWT |
| AI | Anthropic Claude 3.5, Google Gemini Pro |
| Graphic Engine | SVG rendering, 17 templates, 9 background types, typography engine |
| Container | Docker, Docker Compose |