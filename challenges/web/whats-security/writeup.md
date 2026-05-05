# What's Security? — Web Challenge

## Description
A Flask-based 2FA authentication system with an intentional vulnerability.
Players must gain access to the **admin** account to retrieve the flag.

## Vulnerabilities in play
1. **Exposed `.git/config`** — reveals the GitHub repo URL where source code is hosted
2. **Unsalted MD5 passwords** — hashes crackable via CrackStation
3. **OTP leaked in Flask session cookie** — cookie payload is base64, not encrypted; `otp_code` is readable client-side

## Flag
`CodeandCapture{2f4_byp4ss_cl13nt_s1d3_v4l1d4t10n_1s_n0t_s3cur1ty_739182}` — 300 pts

## Intended Solution

1. **Recon** → `GET /.git/config` → reveals `https://github.com/zamine-dots/EventManager-v2`
2. **Read source** → browse repo, find `app.py` → spot `session["otp_code"] = otp`
3. **Crack hashes** → MD5 without salt → crack `admin:admin123` via CrackStation
4. **Login as admin** → triggers 2FA (admin has `two_fa_enabled = 1`)
5. **Decode session cookie** → Flask cookie = `base64(payload).timestamp.sig`
```bash
python3 -c "
import base64, json
cookie = '<paste session cookie here>'
raw = base64.urlsafe_b64decode(cookie.split('.')[0] + '==')
print(json.loads(raw))
"
```
6. **Submit OTP** → server verifies strictly → admin dashboard → **Flag**

## User Matrix

| Username | Password | Role | 2FA? | Dashboard |
|----------------|-------------|----------|------|---------------------|
| admin | admin123 | admin | ✅ | Flag shown |
| operator | password123 | operator | ❌ | Fake incident queue |
| agent_smith | matrix42 | operator | ✅ | Fake incident queue |
| security_chief | letmein | operator | ❌ | Fake incident queue |
| test_user | test123 | operator | ✅ | Fake incident queue |

Players who crack an operator account hit a dead-end dashboard. Only admin has the flag.

