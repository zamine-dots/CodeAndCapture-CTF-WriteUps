"""
The Oracle Speaks — Oracle Server
Run this locally: python3 server.py
It listens on localhost:4444 and answers padding queries.

The server knows the secret key. Players do NOT get the key.
Players send hex-encoded (IV || ciphertext) blobs and get back:
  "VALID"   — padding is correct (PKCS#7)
  "INVALID" — padding is wrong
"""
import socket, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

KEY = bytes.fromhex(open("server_key.bin", "rb").read().hex())

def check_padding(data: bytes) -> bool:
    if len(data) < 32 or len(data) % 16 != 0:
        return False
    iv  = data[:16]
    ct  = data[16:]
    try:
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        unpad(cipher.decrypt(ct), 16)
        return True
    except (ValueError, KeyError):
        return False

def handle(conn):
    try:
        conn.sendall(b"[Oracle] Send hex (IV||CT), newline-terminated:\n")
        buf = b""
        while b"\n" not in buf:
            chunk = conn.recv(1024)
            if not chunk:
                break
            buf += chunk
        line = buf.strip().decode()
        try:
            blob = bytes.fromhex(line)
        except Exception:
            conn.sendall(b"INVALID\n")
            return
        result = check_padding(blob)
        conn.sendall(b"VALID\n" if result else b"INVALID\n")
    finally:
        conn.close()

def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 4444))
    s.listen(5)
    print("[Oracle] Listening on 127.0.0.1:4444 — the Oracle awaits...")
    while True:
        conn, _ = s.accept()
        handle(conn)

if __name__ == "__main__":
    main()
