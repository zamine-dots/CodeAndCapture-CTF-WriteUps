# 🗂️ am secure.Maybe? — Challenge Writeup

**Category:** Cryptography

---

## 📋 Challenge Description

> Agent Zero went dark three days ago. The only thing left behind was a ZIP archive — encrypted, naturally. Our intel team managed to recover a leaked copy of the README file that was bundled inside. Rumour has it the archive was sealed with some *legacy* encryption tool.
>
> Break the lock. Find the flag.
>
> **Files provided:**
> - `lockbox.zip` — the encrypted archive (ZipCrypto, store method)
> - `plain.zip` — a recovered copy of one of the files inside (leaked intel)

---

## 🧠 Concept: What Is This Challenge About?

This challenge is a **Known Plaintext Attack (KPA)** on ZipCrypto — the old, legacy encryption scheme built into the ZIP file format.

The PKZIP stream cipher (ZipCrypto) is notoriously weak. If you know **at least 12 bytes** of one plaintext file that exists inside an encrypted ZIP, you can mathematically recover the internal encryption keys using the **Biham-Kocher attack** — without ever needing to brute-force the actual password.

The tool that does this is [**bkcrack**](https://github.com/kimci86/bkcrack) (Biham-Kocher crack). That's your weapon here.

---

## 🔍 Step 1 — Recon the Archive

First, look at what's inside the encrypted ZIP:

```bash
unzip -l lockbox.zip
```

Output:
```
Archive: lockbox.zip
Length Date Time Name
--------- ---------- ----- ----
40 2026-04-29 11:15 flag.txt
141 2026-04-29 11:15 README.txt
--------- -------
181 2 files
```

Two files: `flag.txt` (what we want) and `README.txt`. The archive is password-protected — trying to extract anything without the password fails.

Now check the encryption method:

```bash
unzip -Z -v lockbox.zip
```

Look for `compression method: none (stored)` and `file security status: encrypted`. The magic words here are **"stored"** — no compression. This means the file bytes inside are almost raw, making the known-plaintext attack much cleaner.

---

## 🛠️ Step 2 — Install bkcrack

Download and build from [github.com/kimci86/bkcrack](https://github.com/kimci86/bkcrack), or grab a precompiled binary from the releases page:

```bash
# Linux example:
wget https://github.com/kimci86/bkcrack/releases/download/v1.7.0/bkcrack-1.7.0-Linux.tar.gz
tar -xzf bkcrack-1.7.0-Linux.tar.gz
cd bkcrack-1.7.0-Linux
```

---

## ⚔️ Step 3 — Run the Known-Plaintext Attack

You have `plain.zip` — a ZIP containing the unencrypted `README.txt`. Use it to attack `lockbox.zip`:

```bash
./bkcrack -C lockbox.zip -c README.txt -P plain.zip -p README.txt
```

**What each flag means:**
- `-C lockbox.zip` — the **C**iphertext (encrypted) archive
- `-c README.txt` — the **c**iphertext entry name inside it
- `-P plain.zip` — the **P**laintext archive (your known copy)
- `-p README.txt` — the **p**laintext entry name inside it

bkcrack will grind through Z-value reduction and key candidates. After a minute or two you'll see something like:

```
[xx:xx:xx] Z reduction using 141 bytes of known plaintext
100.0 % (141 / 141)
[xx:xx:xx] Attack on XXXXXX Z values at index 6
Keys: aabbccdd 11223344 55667788
XX.X % (XXXXXX / XXXXXX)
Found a solution. Stopping.
[xx:xx:xx] Keys aabbccdd 11223344 55667788
```

Those three hex values are your **internal encryption keys**. Write them down.

---

## 🔓 Step 4 — Decrypt the Archive

Now use those keys to dump a fully decrypted copy of the ZIP:

```bash
./bkcrack -C lockbox.zip -k aabbccdd 11223344 55667788 -D unlocked.zip
```

Extract it normally (no password needed since it's been stripped):

```bash
unzip unlocked.zip
cat flag.txt
```

---

## 🏁 Flag

```
CodeandCapture{pl41nt3xt_4tt4cks_m4k3_z1p_cr1ppl3d}
```

---