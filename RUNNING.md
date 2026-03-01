# Running LifeOS 0-21

## Fastest way (Docker)

1. Optional: copy env file and set OpenAI key:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY if desired
```

2. Start all services:

```bash
docker compose up --build
```

3. Open apps:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

## Stop services

```bash
docker compose down
```

## Run without Docker (manual)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lifeos
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
export NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm run dev
```
