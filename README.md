# Automated llms.txt Generator

A production-grade web application that automatically generates and maintains `llms.txt` files for websites by analyzing their structure and content. Built for optimal LLM understanding with real-time WebSocket streaming, scheduled updates, and enterprise-scale infrastructure.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.122-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)

## 🚀 Live Demo

**Production URL:** https://llmstxt.vercel.app/

## 📋 Overview

This tool crawls websites, extracts structured content, and generates `llms.txt` files that help LLMs better index website content. The system includes automated monitoring to keep the generated files synchronized with website changes.

### Key Features

- **Intelligent Crawling**: BFS traversal with configurable depth and page limits
- **JavaScript Support**: Playwright integration for dynamic content via Brightdata
- **Real-time Streaming**: WebSocket-based progress updates and logs
- **LLM Enhancement**: AI-powered content optimization
- **Automated Updates**: Scheduled recrawls via AWS Lambda + EventBridge
- **Persistent Storage**: R2 object storage with public URLs
- **API Security**: API key authentication for WebSocket endpoints
- **Spec Compliance**: Adheres to official llmstxt.org specification
- **Production Ready**: AWS ECS Fargate deployment with auto-scaling

## 🏗️ Architecture

```
┌─────────────────┐
│   Next.js UI    │  (Vercel)
│   WebSocket     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI API    │  (AWS ECS Fargate)
│  WebSocket      │  ← CloudFlare Tunnel
└────────┬────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌──────────┐      ┌──────────────┐
│ Crawler  │      │   Storage    │
│ Playwright      │   Supabase   │
│ Brightdata      │   R2 CDN     │
└──────────┘      └──────────────┘
         ▲
         │
    ┌────┴────┐
    │ Lambda  │  (Scheduled Recrawls)
    │ Cron    │  EventBridge: Every 6h
    └─────────┘
```

## 📊 Tech Stack

**Backend:**
- FastAPI (Python 3.11) - WebSocket API
- Playwright - Browser automation
- BeautifulSoup4 - HTML parsing
- Supabase - PostgreSQL database
- Cloudflare R2 - Object storage
- Brightdata - Proxy for JS-heavy sites

**Frontend:**
- Next.js 15
- TypeScript
- Tailwind CSS
- WebSocket API

**Infrastructure:**
- AWS ECS Fargate - Container orchestration
- AWS ECR - Docker registry
- AWS Application Load Balancer
- AWS Lambda - Scheduled tasks
- AWS EventBridge - Cron scheduling
- Vercel - Frontend hosting
- Terraform - Infrastructure as Code

## 🎯 llms.txt Specification Compliance

The generator adheres to the official specification from [llmstxt.org](https://llmstxt.org/):

- ✅ Markdown format with proper structure
- ✅ Hierarchical headings for sections
- ✅ Blockquote excerpts from pages
- ✅ Clean URL generation (`.md` links when available)
- ✅ Content truncation at semantic boundaries
- ✅ Metadata headers with generation timestamp

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)
- AWS Account (for deployment)
- Supabase Account
- Cloudflare R2 Account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo>
   cd llmstxt
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   playwright install chromium
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local with your backend URL
   ```

4. **Run Development Servers**

   Terminal 1 (Backend):
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📝 Usage

### Web Interface

1. Navigate to the deployed application
2. Enter the target website URL
3. Configure crawl parameters:
   - **Max Pages**: Number of pages to crawl (default: 50)
   - **Description Length**: Character limit for excerpts (default: 500)
   - **Enable Auto-Update**: Schedule periodic recrawls (optional)
   - **Recrawl Interval**: Minutes between updates (default: 360)
   - **LLM Enhancement**: AI-powered optimization (optional)
   - **Use Brightdata**: For JavaScript-heavy sites (optional)
4. Click "Generate llms.txt"
5. Watch real-time crawl progress
6. Download, copy, or view hosted version

### API Usage

**WebSocket Endpoint:** `wss://your-backend.com/ws/crawl?api_key=YOUR_KEY`

**Send:**
```json
{
  "url": "https://example.com",
  "maxPages": 50,
  "descLength": 500,
  "enableAutoUpdate": false,
  "recrawlIntervalMinutes": 360,
  "llmEnhance": false,
  "useBrightdata": false
}
```

**Receive:**
```json
{ "type": "log", "content": "Crawling page 1/50..." }
{ "type": "result", "content": "# Example.com\n\n..." }
{ "type": "url", "content": "https://cdn.example.com/llms.txt" }
{ "type": "error", "content": "Failed to fetch page" }
```

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```bash
# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key

# Storage
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET=llms-txt
R2_PUBLIC_DOMAIN=https://pub-xxx.r2.dev

# Optional Services
BRIGHTDATA_API_KEY=your_brightdata_key
OPENROUTER_API_KEY=your_openrouter_key
LLM_ENHANCEMENT_ENABLED=false

# Security
API_KEY=your_generated_api_key
CRON_SECRET=your_cron_secret

# Application
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/crawl
NEXT_PUBLIC_API_KEY=your_generated_api_key
```

### Generating Secure Keys

```bash
# Generate API key or Cron Secret
openssl rand -base64 32
```

## 🗄️ Database Schema

The application uses Supabase (PostgreSQL) for tracking crawled sites:

```sql
CREATE TABLE crawl_sites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_url TEXT UNIQUE NOT NULL,
    max_pages INTEGER DEFAULT 50,
    desc_length INTEGER DEFAULT 500,
    recrawl_interval_minutes INTEGER DEFAULT 360,
    last_crawled_at TIMESTAMP WITH TIME ZONE,
    llms_txt_url TEXT,
    llms_txt_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_next_crawl ON crawl_sites (
    (last_crawled_at + (recrawl_interval_minutes || ' minutes')::INTERVAL)
);
```

Run the migration:
```bash
psql $DATABASE_URL < backend/migrations/001_create_crawl_sites.sql
```

## 🧪 Testing

```bash
cd backend
pytest -v

## 📦 Deployment

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for comprehensive deployment instructions including:
- AWS infrastructure setup with Terraform
- Docker image building and deployment
- Environment configuration
- DNS and SSL setup
- Monitoring and logs

## 🔒 Security Features

- **API Key Authentication**: WebSocket endpoints require valid API keys
- **CORS Protection**: Configurable origin whitelist
- **Request Validation**: Pydantic models for input validation
- **Rate Limiting**: CloudFlare proxy integration
- **HTTPS/WSS**: TLS encryption for all traffic

## 📊 Monitoring & Logs

**CloudWatch Log Groups:**
- `/ecs/llmstxt-api` - Backend application logs
- `/aws/lambda/llmstxt-auto-update` - Scheduled recrawl logs

**View logs:**
```bash
# ECS logs
aws logs tail /ecs/llmstxt-api --follow

# Lambda logs
aws logs tail /aws/lambda/llmstxt-auto-update --follow
```

## 📚 Project Structure

```
llmstxt/
├── backend/
│   ├── main.py              # FastAPI app + WebSocket
│   ├── config.py            # Environment configuration
│   ├── crawler.py           # Website crawling logic
│   ├── formatter.py         # llms.txt generation
│   ├── storage_supabase.py  # Database operations
│   ├── validator.py         # URL validation
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container
│   ├── migrations/         # Database migrations
│   ├── tests/              # Test suite
│   └── deployment/         # Lambda build scripts
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   └── hooks/         # Custom hooks (WebSocket)
│   ├── package.json
│   ├── Dockerfile
│   └── tailwind.config.ts
├── terraform/
│   ├── main.tf            # Core infrastructure
│   ├── ecs.tf            # ECS cluster + service
│   ├── alb.tf            # Load balancer
│   ├── iam.tf            # IAM roles
│   ├── amplify.tf        # Frontend hosting
│   └── variables.tf      # Configuration
├── README.md             # This file
├── DEPLOYMENT.md         # Deployment guide
└── docker-compose.yml    # Local development
```

## 📄 License

MIT License - See LICENSE file for details
