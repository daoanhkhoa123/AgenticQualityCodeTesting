import re
from typing import Optional

# Coarse, deliberately simple substring/regex blocklist -- not a sandbox, just a
# first line of defense against a drafted *unit test* doing something no unit
# test should need to: delete files, make network calls, or spawn processes /
# execute code dynamically. Matching is case-insensitive.
BLOCKED_PATTERNS: dict[str, str] = {
    # filesystem destruction
    r"\bos\.remove\b": "os.remove (deletes a file)",
    r"\bos\.rmdir\b": "os.rmdir (deletes a directory)",
    r"\bshutil\.rmtree\b": "shutil.rmtree (recursively deletes a directory)",
    r"\.unlink\s*\(": ".unlink( (deletes a file)",
    r"\bsend2trash\b": "send2trash (deletes files)",
    # network access
    r"\bimport\s+requests\b": "import requests (network access)",
    r"\bimport\s+urllib\b": "import urllib (network access)",
    r"\bimport\s+httpx\b": "import httpx (network access)",
    r"\bimport\s+socket\b": "import socket (network access)",
    r"\bimport\s+ftplib\b": "import ftplib (network access)",
    r"\bimport\s+smtplib\b": "import smtplib (network access)",
    # process / dynamic code execution
    r"\bsubprocess\b": "subprocess (spawns processes)",
    r"\bos\.system\b": "os.system (runs a shell command)",
    r"\bos\.popen\b": "os.popen (runs a shell command)",
    r"\beval\s*\(": "eval( (dynamic code execution)",
    r"\bexec\s*\(": "exec( (dynamic code execution)",
    r"__import__\s*\(": "__import__( (dynamic import)",
}


def find_violations(code: Optional[str]) -> list[str]:
    """Scan drafted test source for blocked patterns before it is ever written
    to disk or executed. Returns the matched patterns' human-readable reasons,
    or an empty list if the code looks clean (or is missing).
    """
    if not code:
        return []
    return [reason for pattern, reason in BLOCKED_PATTERNS.items() if re.search(pattern, code, re.IGNORECASE)]
