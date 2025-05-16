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
    if domain in DOMAIN_MAP:
        return DOMAIN_MAP[domain]

    # Break down: subdomain.domain.tld
    parts = domain.split('.')
    if len(parts) < 2:
        return domain

    sub, rest = parts[0], parts[1:]

    sub_code = SUBDOMAIN_MAP.get(sub, sub) if len(parts) > 2 else ''
    tld_code = TLD_MAP.get('.'.join(rest[1:]), TLD_MAP.get(
        rest[-1], rest[-1])) if len(rest) > 1 else ''

    return f"{sub_code}.{rest[0]}.{tld_code}".strip('.')


def decode_domain(encoded: str) -> str:
    if encoded in REVERSE_DOMAIN_MAP:
        return REVERSE_DOMAIN_MAP[encoded]

    parts = encoded.split('.')
    if len(parts) == 3:
        sub, dom, tld = parts
    elif len(parts) == 2:
        sub, dom, tld = '', parts[0], parts[1]
    else:
        return encoded

    sub_real = {v: k for k, v in SUBDOMAIN_MAP.items()}.get(sub, sub)
    tld_real = {v: k for k, v in TLD_MAP.items()}.get(tld, tld)

    return '.'.join(p for p in [sub_real, dom, tld_real] if p)


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

    encoded = f"{proto_code}_{domain_code}_{path_code}"
    return {"code": encoded}


@app.get("/decode/{code}")
def decode_url(code: str):
    try:
        proto_code, domain_code, *path_parts = code.split('_')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid code format")

    protocol = 'https' if proto_code == 's' else 'http'
    domain = decode_domain(domain_code)

    if path_parts:
        try:
            path = decompress_path(path_parts[0])
        except Exception:
            raise HTTPException(
                status_code=400, detail="Failed to decode path")
    else:
        path = ''

    return {"url": f"{protocol}://{domain}{path}"}
