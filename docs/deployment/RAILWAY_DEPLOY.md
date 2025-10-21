# Railway Deployment Guide

## Quick Deploy to Railway

### 1. Prerequisites
- Railway account (https://railway.app)
- Git repository connected to Railway

### 2. Deploy Steps

1. **Create New Project** on Railway
2. **Connect your GitHub repository**
3. **Railway will auto-detect** the Procfile and start deploying
4. **Set Environment Variables** (if needed):
   - No environment variables required for SQLite version

### 3. Important Notes

#### Database
The current setup uses SQLite (`pokemontcg/pokemontcg.db`). For Railway:

**Option A: SQLite with Volume (Simple)**
- Railway will include the database file in deployment
- Data persists with Railway's ephemeral filesystem
- **Limitation**: Data may be lost on redeploy

**Option B: PostgreSQL (Recommended for Production)**
- Add Railway PostgreSQL addon
- Update `pokemontcg/config.py` to use `$DATABASE_URL`
- Migrate data from SQLite to PostgreSQL

#### Files Included
- ✅ `Procfile` - Tells Railway how to start the app
- ✅ `runtime.txt` - Specifies Python version
- ✅ `requirements.txt` - Dependencies
- ✅ `pokemontcg/api.py` - FastAPI application
- ✅ `pokemontcg/pokemontcg.db` - Database (19,653 cards)

### 4. After Deployment

Railway will provide a URL like: `https://your-app.up.railway.app`

**Test your deployed API:**
```bash
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/cards?pageSize=5
```

**View API Documentation:**
- Swagger UI: `https://your-app.up.railway.app/docs`
- ReDoc: `https://your-app.up.railway.app/redoc`

### 5. API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API information |
| `GET /health` | Health check |
| `GET /cards` | Get all cards (paginated) |
| `GET /cards/{id}` | Get specific card |
| `GET /sets` | Get all sets (paginated) |
| `GET /sets/{id}` | Get specific set |
| `GET /types` | Get all Pokemon types |
| `GET /subtypes` | Get all card subtypes |
| `GET /supertypes` | Get all card supertypes |
| `GET /rarities` | Get all card rarities |

### 6. Query Parameters

**Pagination:**
- `page` - Page number (default: 1)
- `pageSize` - Items per page (default: 10, max: 250)

**Filtering (cards endpoint):**
- `name` - Search by card name (partial match)
- `supertype` - Filter by supertype
- `subtype` - Filter by subtype
- `set_id` - Filter by set
- `rarity` - Filter by rarity
- `type` - Filter by Pokemon type

**Examples:**
```bash
# Get Pikachu cards
GET /cards?name=Pikachu

# Get Trainer cards from Base Set
GET /cards?set_id=base1&supertype=Trainer

# Paginate through cards
GET /cards?page=2&pageSize=50
```

### 7. Upgrading to PostgreSQL

If you want to use PostgreSQL for production:

1. **Add PostgreSQL** to your Railway project
2. **Update** `pokemontcg/config.py`:
   ```python
   import os
   DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pokemontcg/pokemontcg.db')
   ```
3. **Migrate data** from SQLite to PostgreSQL
4. **Update** `pokemontcg/api.py` to use SQLAlchemy instead of direct SQLite

### 8. Monitoring

Check your deployment:
- **Railway Dashboard**: View logs and metrics
- **Health Endpoint**: `GET /health` - Shows card/set counts
- **Logs**: Monitor for errors or issues

### 9. Custom Domain

Railway allows custom domains:
1. Go to project settings
2. Add custom domain
3. Configure DNS records

### 10. Troubleshooting

**Build Fails:**
- Check `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt`

**Database Empty:**
- Ensure `pokemontcg/pokemontcg.db` is committed to git
- Check `.gitignore` doesn't exclude `.db` files for deployment

**Port Issues:**
- Railway automatically sets `$PORT` environment variable
- Procfile uses `$PORT` correctly

---

## Current Stats

- **19,653 cards** across **169 sets**
- **11 Pokemon types**
- **173 Pikachu variations**
- **Fast API** with automatic documentation
- **Self-contained** - No external API dependencies

## Support

For issues, check:
- Railway logs
- `/health` endpoint
- API docs at `/docs`
