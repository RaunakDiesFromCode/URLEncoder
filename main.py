from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import brotli
import re

app = FastAPI()


# ---------- DOMAIN MAPPINGS ----------
SUBDOMAIN_MAP = {"www": "w", "blog": "b", "mail": "m"}
TLD_MAP = {"com": "c", "org": "o", "net": "n", "io": "i", "co.uk": "uk"}

# Common domains and shortcuts
DOMAIN_MAP = {
    "google.com": "g",
    "youtube.com": "y",
    "facebook.com": "f",
    "github.com": "gh",
    "openai.com": "oa",
}

REVERSE_DOMAIN_MAP = {v: k for k, v in DOMAIN_MAP.items()}


# ---------- BASE62 ----------
BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def base62_encode_bytes(data: bytes) -> str:
    num = int.from_bytes(data, 'big')
    if num == 0:
        return BASE62_ALPHABET[0]
    encoded = ''
    while num > 0:
        num, rem = divmod(num, 62)
        encoded = BASE62_ALPHABET[rem] + encoded
    return encoded


def base62_decode_to_bytes(s: str) -> bytes:
    num = 0
    for char in s:
        num = num * 62 + BASE62_ALPHABET.index(char)
    byte_length = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_length, 'big')


# ---------- COMPRESSION ----------
def compress_path(path: str) -> str:
    compressed = brotli.compress(path.encode(), quality=11)
    return base62_encode_bytes(compressed)


def decompress_path(encoded: str) -> str:
    compressed = base62_decode_to_bytes(encoded)
    return brotli.decompress(compressed).decode()


# ---------- API MODELS ----------
class URLRequest(BaseModel):
    url: str


# ---------- HELPERS ----------
def encode_domain(domain: str) -> str:
    return base62_encode_bytes(brotli.compress(domain.encode(), quality=11))


def decode_domain(encoded: str) -> str:
    return brotli.decompress(base62_decode_to_bytes(encoded)).decode()



# ---------- ROUTES ----------
@app.post("/encode")
def encode_url(request: URLRequest):
    url = request.url.strip()

    match = re.match(r"(https?)://([^/]+)(/?.*)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid URL format")

    protocol, domain, path = match.groups()
    proto_code = 's' if protocol == 'https' else 'p'
    domain_code = encode_domain(domain)
    path_code = compress_path(path) if path and path != '/' else ''

    parts = [proto_code, domain_code]
    if path_code:
        parts.append(path_code)

    encoded = '-'.join(parts)
    return {"code": encoded}


@app.get("/decode/{code}")
def decode_url(code: str):
    parts = code.split('-')
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid code format")

    proto_code = parts[0]
    domain_code = parts[1]
    path_code = parts[2] if len(parts) > 2 else None

    protocol = 'https' if proto_code == 's' else 'http'

    try:
        domain = decode_domain(domain_code)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to decode domain")

    if path_code:
        try:
            path = decompress_path(path_code)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Failed to decode path")
    else:
        path = ''

    return {"url": f"{protocol}://{domain}{path}"}
