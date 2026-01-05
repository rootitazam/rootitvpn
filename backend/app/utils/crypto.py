from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import base64
import secrets
import string


def generate_reality_keys():
    """Generate Ed25519 key pair for Reality protocol"""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # Serialize keys
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    
    # Convert to base64
    private_key_b64 = base64.b64encode(private_key_bytes).decode('utf-8')
    public_key_b64 = base64.b64encode(public_key_bytes).decode('utf-8')
    
    return private_key_b64, public_key_b64


def generate_short_id(length: int = 8) -> str:
    """Generate a random short ID for Reality"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_uuid() -> str:
    """Generate a UUID for Xray users"""
    import uuid
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

