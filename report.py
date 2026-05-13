import os

# API keys (optional)
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

# Network and concurrency
DEFAULT_TIMEOUT = int(os.getenv("OSINT_TIMEOUT", "10"))
MAX_THREADS = int(os.getenv("OSINT_THREADS", "20"))

# Safety
BATCH_SCAN_THRESHOLD = int(os.getenv("OSINT_BATCH_SCAN_THRESHOLD", "20"))

# External URLs
CRTSH_URL = "https://crt.sh/?q=%25{q}%25&output=json"
IP_API_URL = "http://ip-api.com/json/{ip}"
DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/" 