"""Core OSINT operations (synchronous, thread-safe)"""
from typing import Any, Dict, List, Optional
import socket
import dns.resolver
import re
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests

from . import utils, config

logger = logging.getLogger("osint_pro.core")

PLATFORMS = {
    "GitHub": "https://github.com/{u}",
    "GitLab": "https://gitlab.com/{u}",
    "Bitbucket": "https://bitbucket.org/{u}",
    "Twitter": "https://twitter.com/{u}",
    "Instagram": "https://www.instagram.com/{u}/",
    "VK": "https://vk.com/{u}",
    "Telegram": "https://t.me/{u}",
    "Reddit": "https://www.reddit.com/user/{u}",
    "LinkedIn": "https://www.linkedin.com/in/{u}",
}

COMMON_PORTS = [22, 80, 443, 8080, 3306]
POOL = ThreadPoolExecutor(max_workers=config.MAX_THREADS)


def crtsh_lookup(q: str, max_results: int = 500) -> List[str]:
    """Lookup certificates from crt.sh."""
    url = config.CRTSH_URL.format(q=q)
    data = utils.safe_get_json(url, timeout=15)
    out = set()
    if isinstance(data, list):
        for item in data:
            name = item.get("name_value") or item.get("common_name") or item.get("entry")
            if not name:
                continue
            for ln in str(name).splitlines():
                ln = ln.strip().lstrip("*.")
                if q in ln:
                    out.add(ln)
            if len(out) >= max_results:
                break
    return sorted(out)


def dns_lookup(domain: str) -> Dict[str, List[str]]:
    """Lookup DNS records (A, AAAA, MX, NS, TXT)."""
    resolver = dns.resolver.Resolver()
    types = ["A", "AAAA", "MX", "NS", "TXT"]
    res = {t: [] for t in types}
    for t in types:
        try:
            answers = resolver.resolve(domain, t, lifetime=5)
            for a in answers:
                res[t].append(a.to_text())
        except Exception:
            continue
    return res


def _resolve_a(name: str) -> List[str]:
    """Resolve single A record."""
    out: List[str] = []
    resolver = dns.resolver.Resolver()
    try:
        answers = resolver.resolve(name, "A", lifetime=3)
        for a in answers:
            out.append(a.to_text())
    except Exception:
        pass
    return out


def resolve_many(names: List[str]) -> Dict[str, List[str]]:
    """Resolve many A records in parallel."""
    futures = {POOL.submit(_resolve_a, n): n for n in names}
    out: Dict[str, List[str]] = {}
    for fut in as_completed(futures):
        name = futures[fut]
        try:
            r = fut.result()
            if r:
                out[name] = r
        except Exception:
            continue
    return out


def whois_lookup(domain: str) -> Dict[str, Any]:
    """Lookup whois info (if python-whois installed)."""
    try:
        import whois
        w = whois.whois(domain)
        if hasattr(w, "items"):
            return dict(w)
        return {k: getattr(w, k, None) for k in dir(w) if not k.startswith("_")}
    except ImportError:
        return {"note": "python-whois not installed"}
    except Exception as e:
        return {"error": str(e)}


def _tcp_connect(host: str, port: int, timeout: float) -> bool:
    """Try TCP connect to host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def port_scan(host: str, ports: List[int], concurrency: int = 50, timeout: float = 1.0) -> List[int]:
    """Scan ports (TCP connect)."""
    open_ports: List[int] = []
    with ThreadPoolExecutor(max_workers=min(concurrency, 200)) as ex:
        futures = {ex.submit(_tcp_connect, host, p, timeout): p for p in ports}
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                if fut.result():
                    open_ports.append(p)
            except Exception:
                continue
    return sorted(open_ports)


def ip_geo(ip: str) -> Dict[str, Any]:
    """Get IP geolocation (ipinfo or ip-api)."""
    if config.IPINFO_TOKEN:
        url = f"https://ipinfo.io/{ip}/json"
        try:
            r = requests.get(url, params={"token": config.IPINFO_TOKEN}, timeout=8, headers={"User-Agent": "osint-pro/1.0"})
            if r.status_code == 200:
                return r.json()
            return {"error": f"status {r.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    else:
        url = config.IP_API_URL.format(ip=ip)
        data = utils.safe_get_json(url, timeout=8)
        return data or {}


def _safe_rdns(ip: str) -> Optional[str]:
    """Reverse DNS lookup."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


def probe_username(nick: str, timeout: float = 6.0) -> List[Dict[str, Any]]:
    """Probe username on platforms."""
    results = []
    for name, tpl in PLATFORMS.items():
        url = tpl.format(u=nick)
        try:
            r = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "osint-pro/1.0"})
            status = r.status_code
        except Exception:
            status = "error"
        results.append({"platform": name, "url": url, "status": status})
    return results


def ddg_search_links(query: str, max_results: int = 30) -> List[str]:
    """Search via DuckDuckGo HTML."""
    text = utils.safe_post_text(config.DUCKDUCKGO_HTML, {"q": query}, timeout=10)
    if not text:
        return []
    hrefs = re.findall(r'href="(https?://[^"]+)"', text)
    seen = []
    for h in hrefs:
        if h not in seen:
            seen.append(h)
        if len(seen) >= max_results:
            break
    return seen


def extract_username_from_url(url: str) -> Optional[Dict[str, str]]:
    """Extract username/platform from URL."""
    try:
        p = urlparse(url)
        host = p.netloc.lower()
        path = p.path.strip("/")
        if not path:
            return None
        if "github.com" in host:
            return {"platform": "GitHub", "username": path.split("/")[0]}
        if "gitlab.com" in host:
            return {"platform": "GitLab", "username": path.split("/")[0]}
        if "twitter.com" in host:
            return {"platform": "Twitter", "username": path.split("/")[0]}
        if "instagram.com" in host:
            return {"platform": "Instagram", "username": path.split("/")[0]}
        if host.endswith("vk.com"):
            return {"platform": "VK", "username": path.split("/")[0]}
        if "linkedin.com" in host:
            parts = path.split("/")
            if parts and parts[0] in ("in", "pub"):
                return {"platform": "LinkedIn", "username": parts[1] if len(parts) > 1 else parts[0]}
        if "reddit.com" in host and path.startswith("user/"):
            parts = path.split("/")
            return {"platform": "Reddit", "username": parts[1] if len(parts) > 1 else parts[0]}
        if host in ("t.me", "telegram.me"):
            return {"platform": "Telegram", "username": path.split("/")[0]}
    except Exception:
        return None
    return None


def person_search_by_name(fullname: str) -> Dict[str, Any]:
    """Search person by full name via DuckDuckGo."""
    query = f'"{fullname}" (site:github.com OR site:vk.com OR site:twitter.com OR site:instagram.com OR site:linkedin.com OR site:reddit.com OR site:t.me)'
    links = ddg_search_links(query, max_results=50)
    profiles = {}
    for l in links:
        info = extract_username_from_url(l)
        if info:
            key = (info["platform"], info["username"])
            if key not in profiles:
                profiles[key] = {"platform": info["platform"], "username": info["username"], "url": l}
    return {"query": query, "links_found": links, "profiles": list(profiles.values())}


# High-level gatherers
def gather_domain(target: str, ports: List[int], concurrency: int, do_scan: bool) -> Dict[str, Any]:
    """Gather domain info."""
    domain = target.strip().lower().rstrip("/")
    result: Dict[str, Any] = {"target": domain, "type": "domain"}
    
    whois_fut = POOL.submit(whois_lookup, domain)
    dns_fut = POOL.submit(dns_lookup, domain)
    crt_fut = POOL.submit(crtsh_lookup, domain)
    
    result["whois"] = whois_fut.result(timeout=20)
    dns_res = dns_fut.result(timeout=10)
    result["dns"] = dns_res
    result["crtsh_subdomains"] = crt_fut.result(timeout=20)
    
    subs = result["crtsh_subdomains"][:200]
    result["subdomains_resolved"] = resolve_many(subs) if subs else {}
    
    hosts = dns_res.get("A", [])[:]
    if not hosts and result["subdomains_resolved"]:
        for addrs in result["subdomains_resolved"].values():
            hosts.extend(addrs)
            if hosts:
                break
    
    scan_host = hosts[0] if hosts else None
    result["port_scan_target"] = scan_host
    if do_scan and scan_host:
        result["open_ports"] = port_scan(scan_host, ports, concurrency=concurrency, timeout=1.2)
    else:
        result["open_ports"] = []
    
    # Optional APIs
    if config.SHODAN_API_KEY:
        try:
            r = requests.get("https://api.shodan.io/dns/resolve", params={"hostnames": domain, "key": config.SHODAN_API_KEY}, timeout=8)
            result["shodan"] = r.json() if r.status_code == 200 else {"error": f"status {r.status_code}"}
        except Exception as e:
            result["shodan"] = {"error": str(e)}
    
    if config.VIRUSTOTAL_API_KEY:
        try:
            r = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}", headers={"x-apikey": config.VIRUSTOTAL_API_KEY}, timeout=10)
            result["virustotal"] = r.json() if r.status_code == 200 else {"error": f"status {r.status_code}"}
        except Exception as e:
            result["virustotal"] = {"error": str(e)}
    
    return result


def gather_ip(target: str, ports: List[int], concurrency: int, do_scan: bool) -> Dict[str, Any]:
    """Gather IP info."""
    ip = target.strip()
    result: Dict[str, Any] = {"target": ip, "type": "ip"}
    
    rdns = POOL.submit(_safe_rdns, ip).result(timeout=8)
    result["reverse_dns"] = rdns
    result["geo"] = ip_geo(ip)
    
    if do_scan:
        result["open_ports"] = port_scan(ip, ports, concurrency=concurrency, timeout=1.2)
    else:
        result["open_ports"] = []
    
    if config.SHODAN_API_KEY:
        try:
            r = requests.get(f"https://api.shodan.io/shodan/host/{ip}", params={"key": config.SHODAN_API_KEY}, timeout=8)
            result["shodan"] = r.json() if r.status_code == 200 else {"error": f"status {r.status_code}"}
        except Exception as e:
            result["shodan"] = {"error": str(e)}
    
    if config.VIRUSTOTAL_API_KEY:
        try:
            r = requests.get(f"https://www.virustotal.com/api/v3/ip_addresses/{ip}", headers={"x-apikey": config.VIRUSTOTAL_API_KEY}, timeout=10)
            result["virustotal"] = r.json() if r.status_code == 200 else {"error": f"status {r.status_code}"}
        except Exception as e:
            result["virustotal"] = {"error": str(e)}
    
    return result


def gather_email(target: str) -> Dict[str, Any]:
    """Gather email info."""
    email = target.strip().lower()
    result: Dict[str, Any] = {"target": email, "type": "email"}
    if "@" not in email:
        result["error"] = "invalid email"
        return result
    result["crtsh_hits"] = crtsh_lookup(email)
    return result


def gather_person(target: str) -> Dict[str, Any]:
    """Gather person info (nickname or name search)."""
    t = target.strip()
    result: Dict[str, Any] = {"target": t, "type": "person"}
    if " " in t:
        sr = person_search_by_name(t)
        result.update({"search_type": "name", "query": sr.get("query"), "links_found": sr.get("links_found"), "profiles": sr.get("profiles")})
    else:
        pr = probe_username(t)
        result.update({"search_type": "nickname", "profiles": pr})
    return result