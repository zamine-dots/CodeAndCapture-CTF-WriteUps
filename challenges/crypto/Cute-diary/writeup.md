# 📔 Cute Diary — Challenge Writeup

**Category:** Cryptography


## 📋 CTFd Description

> They said RSA was unbreakable. They never said anything about the *person who set it up.*
>
> Agent Zero kept a diary — encrypted, naturally — using RSA with what they called a "smaller, faster" public exponent. Rookie mistake.
>
> Break their encryption. Read their secrets.
>
> **File:** `challenge.json`

---

## 📁 What You're Given

```json
{
"n": "<1024-bit modulus>",
"e": 3,
"c": "<ciphertext integer>"
}
```

`e = 3`. That's the entire hint you need.

---

## 🧠 The Vulnerability — Small Public Exponent

RSA encryption: `c = m^e mod n`

With `e = 3` and a short message, if `m^3 < n`, the modular reduction **never kicks in**. The ciphertext is literally just `m³` — a plain integer cube. No modulus involved.

To decrypt: take the **integer cube root** of `c`. No key needed.

---

## 🔍 Step 1 — Spot the Weak Exponent

Open `challenge.json`. `e = 3` jumps right out. Check the size of `c` vs `n` — if `c` is significantly smaller than `n`, it's a strong signal that `m^3 < n`.

---

## 🛠️ Step 2 — Install gmpy2

```bash
pip install gmpy2
```

`gmpy2` gives you exact integer nth-root with a flag telling you whether it was exact — crucial for confirming this is the right approach.

---

## ⚔️ Step 3 — Solve

```python
import json, gmpy2
from Crypto.Util.number import long_to_bytes

with open("challenge.json") as f:
d = json.load(f)

c = int(d["c"])
m, exact = gmpy2.iroot(c, 3)

assert exact, "Not exact — cube root didn't land cleanly"
print(long_to_bytes(int(m)).decode())
```

`gmpy2.iroot(c, 3)` returns `(root, is_exact)`. If `is_exact` is `True`, you're done.

---

## 🏁 Flag

```
CodeandCapture{sm4ll_3xp0n3nt_g0_brr}
```