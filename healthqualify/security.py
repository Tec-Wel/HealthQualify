"""Local identity, role authorization and short-lived opaque sessions.

Single-site developer security foundation; not enterprise SSO, MFA, Part 11
identity proofing or a validated identity management system.
"""
from __future__ import annotations
import hashlib
import hmac
import secrets
import sqlite3
import time
from datetime import datetime, timezone

ROLES = {"admin", "qa", "validator", "viewer"}
PERMISSIONS = {
    "admin": {"read", "write", "execute", "baseline", "audit", "users"},
    "qa": {"read", "baseline", "audit"},
    "validator": {"read", "write", "execute"},
    "viewer": {"read"},
}
ITERATIONS = 600_000

class AuthenticationError(PermissionError):
    pass

def password_hash(password: str, salt: bytes) -> str:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS).hex()

class IdentityStore:
    def __init__(self, database: str):
        self.conn = sqlite3.connect(database, timeout=5)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS hq_identities(
          username TEXT PRIMARY KEY, role TEXT NOT NULL, salt TEXT NOT NULL,
          hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS hq_sessions(
          token_hash TEXT PRIMARY KEY, username TEXT NOT NULL REFERENCES hq_identities(username),
          expires INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS hq_security_events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, actor TEXT NOT NULL,
          action TEXT NOT NULL, result TEXT NOT NULL);
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def _event(self, actor: str, action: str, outcome: str):
        self.conn.execute("INSERT INTO hq_security_events(at,actor,action,result) VALUES(?,?,?,?)",
                          (datetime.now(timezone.utc).isoformat(), actor, action, outcome))

    def bootstrap(self, username: str, password: str):
        if self.conn.execute("SELECT 1 FROM hq_identities LIMIT 1").fetchone():
            raise AuthenticationError("Bootstrap unavailable after initial account")
        return self._create(username, password, "admin", "bootstrap")

    def _create(self, username: str, password: str, role: str, actor: str):
        if (not isinstance(username, str) or not 3 <= len(username) <= 64
            or not username.isascii() or not all(c.isalnum() or c in "._-" for c in username)):
            raise ValueError("Username must be 3-64 safe ASCII characters")
        if role not in ROLES or not isinstance(password, str) or len(password) < 12 or len(password) > 256:
            raise ValueError("Invalid role or password length")
        salt = secrets.token_bytes(16)
        with self.conn:
            self.conn.execute("INSERT INTO hq_identities(username,role,salt,hash,active,created_at) VALUES(?,?,?,?,1,?)",
                (username,role,salt.hex(),password_hash(password,salt),datetime.now(timezone.utc).isoformat()))
            self._event(actor,"user.create","success")
        return {"username": username, "role": role}

    def create_user(self, actor: dict, username: str, password: str, role: str):
        self.authorize(actor,"users")
        return self._create(username,password,role,actor["username"])

    def login(self, username: str, password: str, duration: int = 3600) -> str:
        if not isinstance(username,str) or not isinstance(password,str):
            raise AuthenticationError("Invalid credentials")
        row=self.conn.execute("SELECT * FROM hq_identities WHERE username=?",(username,)).fetchone()
        # Always execute comparable password work, including unknown usernames.
        salt=bytes.fromhex(row["salt"]) if row else bytes(16)
        actual=password_hash(password,salt)
        valid=(row is not None and row["active"]==1 and hmac.compare_digest(actual,row["hash"]))
        if not valid:
            with self.conn:self._event("anonymous","login","denied")
            raise AuthenticationError("Invalid credentials")
        if not 60 <= duration <= 3600:
            raise ValueError("Session duration out of bounds")
        token=secrets.token_urlsafe(40)
        with self.conn:
            self.conn.execute("INSERT INTO hq_sessions VALUES(?,?,?,?)",
                (hashlib.sha256(token.encode()).hexdigest(),username,int(time.time())+duration,
                 datetime.now(timezone.utc).isoformat()))
            self._event(username,"login","success")
        return token

    def authenticate(self, token: str) -> dict:
        if not isinstance(token,str) or len(token)<40 or len(token)>128:
            raise AuthenticationError("Missing or invalid token")
        hashed=hashlib.sha256(token.encode()).hexdigest()
        row=self.conn.execute("""SELECT u.username,u.role,u.active,s.expires FROM hq_sessions s
          JOIN hq_identities u ON u.username=s.username WHERE s.token_hash=?""",(hashed,)).fetchone()
        if not row or row["active"]!=1 or row["expires"]<=int(time.time()):
            raise AuthenticationError("Session invalid or expired")
        return {"username":row["username"],"role":row["role"]}

    def authorize(self, principal: dict, action: str):
        if not isinstance(principal,dict) or action not in PERMISSIONS.get(principal.get("role"),set()):
            raise AuthenticationError("Insufficient permission")

    def logout(self, token: str):
        if not isinstance(token,str):
            raise AuthenticationError("Invalid session")
        with self.conn:
            self.conn.execute("DELETE FROM hq_sessions WHERE token_hash=?",
                              (hashlib.sha256(token.encode()).hexdigest(),))
