# 📮 Postdude — Challenge Writeup

**Category:** Cryptography

## 📋 CTFd Description

> A postcard arrived at HQ addressed to no one in particular. The message on the front is scrambled — some kind of cipher. But Agent Zero always said: *"The picture tells half the story."*
>
> Maybe look a little deeper than the surface.
>
> **Files:** `postcard.jpg`, `message.txt`

---

## 📁 What You're Given

- `postcard.jpg` — an image of a postcard with a garbled message on it
- `message.txt` — the ciphertext in plain text: `FouorbrOdpkeis{j1sq3r3_d3d4u4h4_gx3xty}`

The ciphertext looks almost like a flag — the `{}` structure is preserved, numbers and special characters are unchanged, but letters have been shifted. Classic **Vigenère cipher**.

---

## 🧠 The Vulnerability — Key Hidden in EXIF

The Vigenère cipher is only as strong as its key. The key was carelessly left inside the image's **EXIF metadata** — the hidden fields cameras and tools embed in JPEG files (camera make/model, timestamps, GPS, comments, etc.).

---

## 🔍 Step 1 — Inspect the Image Metadata

Use any EXIF reader:

```bash
# Option 1: exiftool (recommended)
exiftool postcard.jpg

# Option 2: Python
python3 -c "
import piexif
d = piexif.load('postcard.jpg')
print(d['Exif'][37510]) # 37510 = UserComment field
"
```

Look for the `UserComment` field. You'll find:

```
DevelopmentKey:DARKROOM
```

The key is `DARKROOM`.

---

## ⚔️ Step 2 — Decrypt the Vigenère

```python
def vigenere_decrypt(ct, key):
key = key.upper()
result = []
ki = 0
for ch in ct:
if ch.isalpha():
shift = ord(key[ki % len(key)]) - ord('A')
base = ord('A') if ch.isupper() else ord('a')
result.append(chr((ord(ch) - base - shift) % 26 + base))
ki += 1
else:
result.append(ch)
return ''.join(result)

ct = open("message.txt").read().strip()
key = "DARKROOM"
print(vigenere_decrypt(ct, key))
```

---

## 🏁 Flag

```
CodeandCapture{v1gn3r3_m3t4d4t4_sl3uth}
```

