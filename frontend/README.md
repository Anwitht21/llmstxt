# Frontend - llms.txt Generator

Next.js frontend with WebSocket integration for real-time crawl monitoring.

## Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
npm start
```

## Features

- Real-time WebSocket log streaming
- Configurable crawl parameters (URL, max pages, snippet length)
- Download generated llms.txt
- Copy to clipboard
- View hosted URL (if storage configured)
- Dark theme UI
- Responsive design
