"""One-time Google OAuth setup for Calendar + Sheets.

Usage:
  cd services/backend
  .venv\\Scripts\\python scripts/google_oauth_setup.py

Place your downloaded OAuth client JSON as google-oauth-client.json first.
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from dotenv import load_dotenv

load_dotenv(BACKEND_ROOT / '.env')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
]

CLIENT_FILE = BACKEND_ROOT / 'google-oauth-client.json'
TOKEN_FILE = BACKEND_ROOT / 'google-oauth-token.json'
PREFERRED_PORTS = (8090, 8765, 8888, 8080, 0)


def _pick_free_port() -> int:
    for port in PREFERRED_PORTS:
        if port == 0:
            return 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('localhost', port))
                return port
            except OSError:
                continue
    return 0


def main() -> None:
    if not CLIENT_FILE.exists():
        print(f'Fichier manquant: {CLIENT_FILE}')
        print('Renommez votre JSON OAuth téléchargé en google-oauth-client.json')
        sys.exit(1)

    credentials = None
    if TOKEN_FILE.exists():
        try:
            credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except ValueError:
            print('Ancien token invalide (refresh_token manquant), nouvelle connexion requise.')
            credentials = None

    if credentials and credentials.valid and credentials.refresh_token:
        print('Token OAuth déjà valide:', TOKEN_FILE)
        return

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_FILE), SCOPES)
        port = _pick_free_port()
        redirect_uri = f'http://localhost:{port}/' if port else '(port dynamique — voir URL dans le terminal)'
        print('Ouverture du navigateur pour autoriser Google Calendar + Sheets…')
        print(f'Port local: {port}')
        print(f'URI de redirection: {redirect_uri}')
        print('Ajoutez cette URI dans Google Cloud > Credentials > Authorized redirect URIs')
        print('(Fermez les autres scripts OAuth en cours si le port était occupé.)')
        credentials = flow.run_local_server(
            port=port,
            open_browser=True,
            access_type='offline',
            prompt='consent',
        )

    if not credentials.refresh_token:
        print('ERREUR: Google n\'a pas renvoye de refresh_token.')
        print('Supprimez google-oauth-token.json et relancez ce script.')
        sys.exit(1)

    TOKEN_FILE.write_text(credentials.to_json(), encoding='utf-8')
    print(f'Token enregistré: {TOKEN_FILE}')
    print('Redémarrez le backend (py main.py) puis testez un rendez-vous.')


if __name__ == '__main__':
    main()
