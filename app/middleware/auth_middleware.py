import base64
import falcon
from pathlib import Path
import json

def load_auth_config():
    auth_file = Path(__file__).parent / "auth.json" 
    if not auth_file.exists():
        return None
    try:
        return json.loads(auth_file.read_text())
    except Exception:
        return None

class BasicAuthMiddleware:
    def __init__(self):
        self.creds = load_auth_config()
        self.realm = "MemoryHack"
        
    def process_request(self, req, resp):
        if req.path.startswith('/resources/static'):
            return
            
        if not self.creds:
            return
            
        auth_header = req.get_header('Authorization')
        
        if not auth_header or not auth_header.startswith('Basic '):
            raise falcon.HTTPUnauthorized(
                title='Authentication required',
                description='Please provide valid credentials',
                challenges=[f'Basic realm="{self.realm}"']
            )
            
        # Extract and decode credentials
        encoded_credentials = auth_header[6:]
        try:
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
        except (ValueError, UnicodeDecodeError, base64.binascii.Error):
            raise falcon.HTTPUnauthorized(
                title='Invalid credentials',
                description='Could not decode credentials',
                challenges=[f'Basic realm="{self.realm}"']
            )
            
        # Validate credentials
        if username != self.creds.get("username") or password != self.creds.get("password"):
            raise falcon.HTTPUnauthorized(
                title='Invalid credentials',
                description='Username or password incorrect',
                challenges=[f'Basic realm="{self.realm}"']
            )
            
        # Authentication successful
        req.context.user = {"username": username}