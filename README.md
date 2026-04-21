# Lunar Life Research Database

月面基地での生活課題と、それに応える世界中の技術・研究・プロジェクトを集めたデータベース。JAXA「Space Life on the Moon」をベースに構築。

## Tech Stack

- **Database**: SQLite (data/lunar_life.db)
- **Collection**: Python scripts (Claude API)
- **Dashboard**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Deploy**: Vercel (static export)

## Categories (10)

食 / 水 / 衛生 / 医療 / 運動 / 衣服 / 通信 / 娯楽 / 睡眠・住環境 / 作業環境

## Setup

```bash
# Initialize DB
python3 scripts/init_db.py

# Collect data
python3 scripts/collect_seed.py
python3 scripts/collect_web.py
python3 scripts/collect_papers.py

# Export to JSON
python3 scripts/export_json.py

# Run dashboard
cd web && npm install && npm run dev
```

## Scripts

| Script | Purpose |
|--------|---------|
| `init_db.py` | Create SQLite schema |
| `collect_seed.py` | Generate 50 seed entries via Claude API |
| `collect_web.py` | Generate 200 deep-dive entries |
| `collect_papers.py` | Generate 50 academic paper entries |
| `export_json.py` | Export SQLite to JSON for dashboard |
