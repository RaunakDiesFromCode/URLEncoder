from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import brotli
import re

app = FastAPI()

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

def compress_path(path: str) -> str:
    compressed = brotli.compress(path.encode(), quality=11)
    return base62_encode_bytes(compressed)

def decompress_path(encoded: str) -> str:
    compressed = base62_decode_to_bytes(encoded)
    return brotli.decompress(compressed).decode()

class URLRequest(BaseModel):
    url: str

def encode_domain(domain: str) -> str:
    return base62_encode_bytes(brotli.compress(domain.encode(), quality=11))

def decode_domain(encoded: str) -> str:
    return brotli.decompress(base62_decode_to_bytes(encoded)).decode()


@app.post("/encode")
def encode_url(request: URLRequest):
    url = request.url.strip()
    match = re.match(r"(https?)://([^/]+)(/?.*)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid URL format")

    protocol, domain, path = match.groups()
    proto_code = 'S' if protocol == 'https' else 'P'
    domain_code = encode_domain(domain)

    # Optimize Brotli compression for path
    path_code = ''
    if path and path != '/':
        path_bytes_11 = brotli.compress(path.encode(), quality=11)
        path_bytes_5 = brotli.compress(path.encode(), quality=5)
        path_compressed = min(path_bytes_11, path_bytes_5, key=len)
        path_code = base62_encode_bytes(path_compressed)

    encoded = proto_code + domain_code
    if path_code:
        encoded += path_code  # No separator
    return {"code": encoded}


@app.get("/decode/{code}")
def decode_url(code: str):
    if len(code) < 2:
        raise HTTPException(status_code=400, detail="Invalid code format")

    proto_code = code[0]
    rest = code[1:]

    # Heuristic: domain ends where decompression succeeds
    # Try progressive slices to decode domain
    for i in range(1, len(rest)):
        try:
            domain = decode_domain(rest[:i])
            domain_code = rest[:i]
            path_code = rest[i:] if i < len(rest) else ''
            break
        except Exception:
            continue
    else:
        raise HTTPException(status_code=400, detail="Failed to decode domain")

    protocol = 'https' if proto_code == 'S' else 'http'

    if path_code:
        try:
            path = decompress_path(path_code)
        except Exception:
            raise HTTPException(
                status_code=400, detail="Failed to decode path")
    else:
        path = ''

    return {"url": f"{protocol}://{domain}{path}"}
