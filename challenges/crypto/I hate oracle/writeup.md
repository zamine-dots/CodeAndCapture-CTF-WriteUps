# 🔮 I hate oracle — Challenge Writeup

**Category:** Cryptography
---


## 📋 CTFd Description

> Deep inside the encrypted archives of Agency Zero lives a service that will answer one question, and one question only:
>
> *"Is the padding correct?"*
>
> That's all it says. That's all it needs to say.
>
> The flag was encrypted with AES-128-CBC. The key is locked away. But the Oracle is listening.
>
> **Files:** `ciphertext.txt`, `server.py`, `server_key.bin`
>
> **Setup:** `python3 server.py` (runs locally on port 4444)

---

## 📁 What You're Given

- `ciphertext.txt` — hex-encoded `IV || ciphertext` (AES-CBC, 16-byte blocks)
- `server.py` — the oracle server; run it locally
- `server_key.bin` — the AES key (used by the server only; don't peek 👀)

The oracle accepts a hex-encoded `IV || ciphertext` blob and replies `VALID` or `INVALID` based purely on whether the PKCS#7 padding decrypts correctly. Nothing else leaks.

---

## 🧠 The Vulnerability — CBC Padding Oracle

**CBC decryption** of block `i`:

```
Plaintext[i] = AESDecrypt(Ciphertext[i]) XOR Ciphertext[i-1]
```

The last block must end with valid PKCS#7 padding:
- 1 byte of `\x01`, or
- 2 bytes of `\x02\x02`, or
- ... up to 16 bytes of `\x10` × 16

If we **control** `Ciphertext[i-1]` and flip bytes in it, we change what `Plaintext[i]` looks like after decryption — without changing what `AESDecrypt(Ciphertext[i])` produces (we call this the *intermediate value*).

We exploit this to recover the intermediate value byte by byte, then XOR it with the real `Ciphertext[i-1]` to get the actual plaintext.

**This only requires the ability to ask: "Is the padding valid?" — nothing more.**

---

## 🛠️ Setup

```bash
# Terminal 1 — start the oracle
python3 server.py

# Terminal 2 — run the solver
python3 solve.py
```

---

## ⚔️ The Attack — Step by Step

### Parse the ciphertext

```python
raw = bytes.fromhex(open("ciphertext.txt").read().strip())
iv = raw[:16]
ct = raw[16:]
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
prevs = [iv] + blocks[:-1]
```

### Recover one block

For each ciphertext block `C`, with its predecessor `P` (or the IV):

**Goal:** find `intermediate[j]` = `AESDecrypt(C)[j]` for each byte position `j`.

Work **right to left** (byte 15 → 0):

```
target_pad = 16 - j # e.g. \x01 for last byte, \x02\x02 for last two
```

For byte position `j`:
1. Build a crafted 16-byte prefix. Set bytes after `j` so they XOR with already-known intermediate values to produce `target_pad`.
2. Brute-force byte `j` from 0–255.
3. When the oracle says `VALID`, you found the byte where `crafted[j] XOR intermediate[j] == target_pad`.
4. So: `intermediate[j] = crafted[j] XOR target_pad`.

Once you have `intermediate[j]`, the real plaintext byte is:

```
plaintext[j] = intermediate[j] XOR P[j]
```

### Edge case — last byte ambiguity

When targeting the last byte (`j = 15`), a guess of `\x01` might hit valid padding even if the byte was supposed to be `\x02` in a two-byte sequence. Guard against this by also flipping the second-to-last byte and checking if the oracle still says `VALID`. If it flips to `INVALID`, your guess was a false positive — keep searching.

---

## 🔮 Full Solve Script

```python
import socket

BLOCK = 16
HOST, PORT = "127.0.0.1", 4444

def oracle(iv, ct):
blob = (iv + ct).hex() + "\n"
with socket.create_connection((HOST, PORT), timeout=5) as s:
s.recv(256)
s.sendall(blob.encode())
return s.recv(16).strip() == b"VALID"

def decrypt_block(prev, ct_block):
intermediate = bytearray(BLOCK)
for j in range(BLOCK - 1, -1, -1):
pad_val = BLOCK - j
crafted = bytearray(BLOCK)
for k in range(j + 1, BLOCK):
crafted[k] = intermediate[k] ^ pad_val
for guess in range(256):
crafted[j] = guess
if oracle(bytes(crafted), ct_block):
if j == BLOCK - 1: # edge case check
crafted[j-1] ^= 1
if not oracle(bytes(crafted), ct_block):
crafted[j-1] ^= 1
continue
crafted[j-1] ^= 1
intermediate[j] = guess ^ pad_val
break
return bytes(intermediate[i] ^ prev[i] for i in range(BLOCK))

raw = bytes.fromhex(open("ciphertext.txt").read().strip())
iv = raw[:BLOCK]
ct = raw[BLOCK:]
blks = [ct[i:i+BLOCK] for i in range(0, len(ct), BLOCK)]
prevs = [iv] + blks[:-1]

pt = b""
for i, (p, b) in enumerate(zip(prevs, blks)):
print(f"[*] Block {i+1}/{len(blks)}...")
pt += decrypt_block(p, b)

pad = pt[-1]
print(pt[:-pad].decode())
```

---

## 🏁 Flag

```
CodeandCapture{p4dd1ng_0r4cl3_wh1sp3r3d_my_s3cr3ts}
```

---