# Phantom Includes - CTF Challenge

**Category:** Web Exploitation

Step 1: Reconnaissance
They visit the site and notice the URL pattern:
http://CodeandCapture:8080/index.php?page=home

The page parameter immediately signals a potential file inclusion vulnerability.

Step 2: Test for LFI
They try a classic path traversal:
?page=../../../../etc/passwd

It fails — the sanitization strips ../. But the error message is the key hint it reveals :
"failed to open stream: flag.php"

This confirms:

Files are included with .php appended
The parameter feeds directly into include()
Step 3: Identify the Dead End
They try ?page=flag — the file executes but shows nothing, because the flag is stored in a PHP variable or comment, not echoed to the page. They need the source code, not the output.

Step 4: The "Aha" Moment — PHP Wrappers
A seasoned CTF player or someone who searches "LFI read PHP source code" finds php://filter. The key insight is:

PHP stream wrappers are processed before the extension is appended conceptually — and include() accepts full wrapper URIs, not just filenames.

They craft:
?page=php://filter/read=convert.base64-encode/resource=flag

The server executes:
include("php://filter/.../resource=flag.php")

The wrapper intercepts, base64-encodes the raw file bytes, and outputs them as text instead of executing PHP.

Step 5: Decode the Output
The page now contains a base64 blob. They decode it:

echo "PD9waHAK..." | base64 -d

This reveals the PHP source containing the flag.

The Learning Curve

Beginner: Struggles unless they know to search for "LFI php filter wrapper CTF"
Intermediate: Recognizes the pattern from prior CTF experience
Expert: Identifies it immediately from the ?page= parameter

