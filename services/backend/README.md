# Backend

Flask API for the AI consulting platform.

Main features:
- JWT auth with refresh tokens
- Lead qualification and scoring
- Appointment scheduling primitives
- Knowledge base and proposal scaffolding
- OpenAPI spec at `/api/openapi.json`
- Realtime consultant events through Socket.IO

Run locally:

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env      # Windows — puis éditez DATABASE_URL
python main.py

The `.env` file in this folder is loaded automatically at startup.
Tables are created in PostgreSQL via `db.create_all()` on first run (database must exist beforehand).

### Google Calendar + Sheets (OAuth)

1. Google Cloud → Credentials → **OAuth client ID** (Desktop app).
2. Download the JSON and save it as `google-oauth-client.json` in this folder.
3. Run once:
   `python scripts/google_oauth_setup.py`
4. Set in `.env`:
   - `GOOGLE_CALENDAR_ID=your@gmail.com` (or `primary`)
   - `GOOGLE_SHEETS_ID=<spreadsheet id from URL>`
   - `GOOGLE_SHEETS_RANGE=Rendez-vous!A:H`
