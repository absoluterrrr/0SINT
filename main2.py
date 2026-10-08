#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
0SINT v5 — passive OSINT helper
Автор интерфейса: Niekocham

Возможности:
  1. Поиск публичных профилей по username
  2. Информация о домене + DNS + WHOIS
  3. Информация об IP
  4. Проверка email (формат, Gravatar, HIBP при наличии API key)
  5. OSINT по номеру телефона (только публичные метаданные)
  6. Генерация текстового отчёта

Установка:
  pip install requests phonenumbers python-whois dnspython

Не выполняет вход, подбор паролей, эксплуатацию уязвимостей или
получение приватных данных.
"""

import hashlib
import ipaddress
import json
import os
import re
import socket
import time
import webbrowser
from datetime import datetime
from urllib.parse import quote, quote_plus

import requests

try:
    import whois
except ImportError:
    whois = None

try:
    import dns.resolver
except ImportError:
    dns = None

try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
except ImportError:
    phonenumbers = None
    carrier = geocoder = timezone = None


# =========================================================
# COLORS
# =========================================================

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
WHITE = "\033[37m"
BOLD = "\033[1m"
RESET = "\033[0m"

TIMEOUT = 8
HEADERS = {
    "User-Agent": "0SINT/5.0 (passive OSINT; educational use)"
}

LAST_REPORT = []


# =========================================================
# HELPERS
# =========================================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n{CYAN}Нажмите Enter чтобы продолжить...{RESET}")


def ask(prompt):
    return input(f"{YELLOW}{prompt}{RESET}").strip()


def add_report(text):
    LAST_REPORT.append(str(text))


def show(title, value, color=GREEN):
    print(f"{color}[+] {title}: {WHITE}{value}{RESET}")
    add_report(f"{title}: {value}")


def valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9._-]{1,64}", username))


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def normalize_domain(domain):
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]
    domain = domain.split(":")[0]
    return domain.strip(".")


def open_url(url):
    try:
        webbrowser.open(url)
        print(f"{GREEN}[+] Открыто: {url}{RESET}")
    except Exception:
        print(f"{YELLOW}[!] Скопируй URL вручную: {url}{RESET}")


def safe_get(url, **kwargs):
    kwargs.setdefault("timeout", TIMEOUT)
    kwargs.setdefault("headers", HEADERS)
    try:
        return requests.get(url, **kwargs)
    except requests.RequestException:
        return None


# =========================================================
# BANNER
# =========================================================

def banner():
    clear()
    print(f"""{RED}{BOLD}
 ██████╗ ███████╗██╗███╗   ██╗████████╗
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
██║   ██║███████╗██║██╔██╗ ██║   ██║
██║   ██║╚════██║██║██║╚██╗██║   ██║
╚██████╔╝███████║██║██║ ╚████║   ██║
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝
{CYAN}             OSINT TOOL v5
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{GREEN} Creator : Niekocham
{GREEN} Python  : 3.x
{GREEN} Mode    : PASSIVE OSINT
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{RESET}""")


def loading():
    print(f"{YELLOW}Загрузка модулей", end="", flush=True)
    for _ in range(4):
        time.sleep(0.15)
        print(".", end="", flush=True)
    print(f" {GREEN}[OK]{RESET}")


# =========================================================
# USERNAME
# =========================================================

def username_platforms(username):
    u = quote(username, safe="")
    return {
        "GitHub": f"https://github.com/{u}",
        "SoundCloud": f"https://soundcloud.com/{u}",
        "Roblox": f"https://www.roblox.com/user.aspx?username={u}",
        "Linktree": f"https://linktr.ee/{u}",
        "Behance": f"https://www.behance.net/{u}",
        "Gravatar": f"https://gravatar.com/{u}",
        "DEV": f"https://dev.to/{u}",
    }


def check_username(username):
    if not valid_username(username):
        print(f"{RED}[!] Некорректный username. Разрешены A-Z, 0-9, '.', '_' и '-'.{RESET}")
        return

    print(f"\n{BLUE}=== Поиск публичных профилей: {username} ==={RESET}\n")
    add_report(f"USERNAME: {username}")

    found = 0
    for platform, url in username_platforms(username).items():
        response = safe_get(url, allow_redirects=True)

        if response is None:
            print(f"{YELLOW}[?] {platform}: нет ответа{RESET}")
            continue

        # У разных сайтов нет единого стандарта 404, поэтому это
        # именно HTTP-индикатор, а не гарантия существования аккаунта.
        if response.status_code == 200:
            print(f"{GREEN}[+] {platform}{RESET}")
            print(f"    {url}")
            add_report(f"[+] {platform}: {url}")
            found += 1
        elif response.status_code in (401, 403, 404, 410, 429, 999):
            continue
        else:
            continue

    print(f"\n{CYAN}Результат: HTTP-проверка завершена, потенциальных совпадений: {found}{RESET}")
    print(f"{YELLOW}Важно: 200 не всегда означает реальный профиль — сайт мог вернуть свою страницу-заглушку.{RESET}")


# =========================================================
# IP LOOKUP
# =========================================================

def ip_lookup(ip):
    print(f"\n{BLUE}=== Информация об IP: {ip} ==={RESET}\n")

    try:
        obj = ipaddress.ip_address(ip)
    except ValueError:
        print(f"{RED}[!] Некорректный IP-адрес.{RESET}")
        return

    add_report(f"IP: {ip}")
    show("Тип", "IPv4" if obj.version == 4 else "IPv6")
    show("Private", obj.is_private)
    show("Global", obj.is_global)
    show("Loopback", obj.is_loopback)

    response = safe_get(f"https://ipwho.is/{quote(ip, safe='')}")
    if not response:
        print(f"{RED}[!] Сервис IP-информации недоступен.{RESET}")
        return

    try:
        data = response.json()
    except ValueError:
        print(f"{RED}[!] Сервис вернул некорректный JSON.{RESET}")
        return

    if not data.get("success", False):
        print(f"{RED}[-] IP-информация не найдена.{RESET}")
        return

    show("Страна", data.get("country", "—"))
    show("Регион", data.get("region", "—"))
    show("Город", data.get("city", "—"))
    show("Почтовый индекс", data.get("postal", "—"))
    show("Часовой пояс", (data.get("timezone") or {}).get("id", "—"))
    show("Провайдер", (data.get("connection") or {}).get("isp", "—"))
    show("ASN", (data.get("connection") or {}).get("asn", "—"))
    show("Организация", (data.get("connection") or {}).get("org", "—"))
    show("Reverse DNS", socket.getfqdn(ip))


# =========================================================
# EMAIL
# =========================================================

def email_lookup(email):
    print(f"\n{BLUE}=== Проверка Email: {email} ==={RESET}\n")

    email = email.lower().strip()
    if not valid_email(email):
        print(f"{RED}[!] Некорректный email.{RESET}")
        return

    add_report(f"EMAIL: {email}")
    show("Формат", "корректный")

    local, domain = email.split("@", 1)
    show("Домен", domain)

    # Gravatar: публичный хешированный идентификатор.
    digest = hashlib.md5(email.encode("utf-8")).hexdigest()
    gravatar = f"https://www.gravatar.com/avatar/{digest}?d=404"
    response = safe_get(gravatar)

    if response and response.status_code == 200:
        show("Gravatar", f"https://www.gravatar.com/{digest}")
    else:
        print(f"{YELLOW}[-] Gravatar: публичный профиль не найден{RESET}")

    # MX-записи.
    if dns is not None:
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=5)
            mx = sorted(str(x.exchange).rstrip(".") for x in answers)
            show("MX", ", ".join(mx))
        except Exception:
            print(f"{YELLOW}[-] MX-записи не получены{RESET}")
    else:
        print(f"{YELLOW}[!] dnspython не установлен — MX пропущен{RESET}")

    # HIBP требует API key. Ключ не хранится в коде.
    hibp_key = os.getenv("HIBP_API_KEY")
    if hibp_key:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote(email, safe='')}"
        headers = {
            **HEADERS,
            "hibp-api-key": hibp_key,
            "user-agent": "0SINT/5.0"
        }
        response = safe_get(url, headers=headers, params={"truncateResponse": "false"})
        if response and response.status_code == 200:
            try:
                breaches = response.json()
                show("HIBP", f"найдено утечек: {len(breaches)}")
                for breach in breaches:
                    print(f"    {YELLOW}• {breach.get('Name', 'Unknown')}{RESET}")
                    add_report(f"HIBP: {breach.get('Name', 'Unknown')}")
            except ValueError:
                print(f"{YELLOW}[!] HIBP вернул некорректный ответ{RESET}")
        elif response and response.status_code == 404:
            show("HIBP", "утечки для адреса не найдены")
        elif response:
            print(f"{YELLOW}[!] HIBP HTTP {response.status_code}{RESET}")
    else:
        print(f"{YELLOW}[i] HIBP: API-ключ не задан, проверка пропущена.{RESET}")
        print(f"{WHITE}    Переменная окружения: HIBP_API_KEY{RESET}")


# =========================================================
# PHONE
# =========================================================

def phone_lookup(phone):
    print(f"\n{BLUE}=== Phone OSINT: {phone} ==={RESET}\n")

    if phonenumbers is None:
        print(f"{RED}[!] Установи phonenumbers: pip install phonenumbers{RESET}")
        return

    try:
        parsed = phonenumbers.parse(phone, None)
    except phonenumbers.NumberParseException as e:
        print(f"{RED}[!] Не удалось разобрать номер: {e}{RESET}")
        return

    if not phonenumbers.is_valid_number(parsed):
        print(f"{RED}[-] Номер невалиден.{RESET}")
        return

    add_report(f"PHONE: {phone}")
    show("Номер", phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    ))
    show("Страна/регион", geocoder.description_for_number(parsed, "ru") or "—")
    show("Оператор", carrier.name_for_number(parsed, "ru") or "—")

    zones = timezone.time_zones_for_number(parsed)
    show("Timezone", ", ".join(zones) if zones else "—")

    country_code = parsed.country_code
    national = parsed.national_number
    show("Country code", f"+{country_code}")
    show("National number", national)

    print(f"\n{CYAN}Публичные ссылки для ручной проверки:{RESET}")
    q = quote_plus(phone)
    links = {
        "Google": f"https://www.google.com/search?q={q}",
        "Bing": f"https://www.bing.com/search?q={q}",
        "DuckDuckGo": f"https://duckduckgo.com/?q={q}",
        "WhatsApp": f"https://wa.me/{phone.lstrip('+').replace(' ', '')}",
    }

    for name, url in links.items():
        print(f"{GREEN}[+] {name}{RESET}: {url}")
        add_report(f"{name}: {url}")


# =========================================================
# DOMAIN / DNS / WHOIS
# =========================================================

def dns_records(domain):
    if dns is None:
        print(f"{YELLOW}[!] dnspython не установлен — DNS пропущен.{RESET}")
        return

    for record_type in ("A", "AAAA", "MX", "NS", "TXT"):
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=5)
            values = [str(x).strip() for x in answers]
            print(f"{GREEN}[+] {record_type}:{RESET} {', '.join(values)}")
            add_report(f"DNS {record_type}: {', '.join(values)}")
        except Exception:
            print(f"{YELLOW}[-] {record_type}: нет данных{RESET}")


def get_domain_info(domain):
    domain = normalize_domain(domain)
    print(f"\n{BLUE}=== Домен: {domain} ==={RESET}\n")

    if not domain or "." not in domain:
        print(f"{RED}[!] Некорректный домен.{RESET}")
        return

    add_report(f"DOMAIN: {domain}")

    try:
        addresses = socket.getaddrinfo(domain, None)
        ips = sorted({item[4][0] for item in addresses})
        for ip in ips:
            show("IP", ip)
    except socket.gaierror:
        print(f"{RED}[-] DNS не разрешает домен.{RESET}")

    print(f"\n{CYAN}--- DNS ---{RESET}")
    dns_records(domain)

    if whois is None:
        print(f"\n{YELLOW}[!] python-whois не установлен — WHOIS пропущен.{RESET}")
        return

    print(f"\n{CYAN}--- WHOIS ---{RESET}")
    try:
        info = whois.whois(domain)

        for title, key in (
            ("Домен", "domain_name"),
            ("Регистратор", "registrar"),
            ("Создан", "creation_date"),
            ("Истекает", "expiration_date"),
            ("Обновлён", "updated_date"),
            ("Статус", "status"),
            ("Name servers", "name_servers"),
        ):
            value = getattr(info, key, None)
            if value:
                if isinstance(value, (list, tuple, set)):
                    value = ", ".join(map(str, value))
                show(title, value, CYAN)
    except Exception as e:
        print(f"{RED}[!] WHOIS ошибка: {e}{RESET}")


# =========================================================
# REPORT
# =========================================================

def save_report():
    if not LAST_REPORT:
        print(f"{YELLOW}[!] Отчёт пока пуст.{RESET}")
        return

    filename = f"osint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("0SINT v5 REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Created: {datetime.now().isoformat(timespec='seconds')}\n\n")
            f.write("\n".join(LAST_REPORT))
            f.write("\n")
        print(f"{GREEN}[+] Отчёт сохранён: {os.path.abspath(filename)}{RESET}")
    except OSError as e:
        print(f"{RED}[!] Ошибка сохранения: {e}{RESET}")


# =========================================================
# MENU
# =========================================================

def menu():
    banner()
    print(f"""
{WHITE}╔══════════════════════════════════════╗
║          {CYAN}{BOLD}ГЛАВНОЕ МЕНЮ{WHITE}               ║
╠══════════════════════════════════════╣
║ {GREEN}[1]{WHITE} Поиск username                    ║
║ {GREEN}[2]{WHITE} Информация о домене + DNS/WHOIS  ║
║ {GREEN}[3]{WHITE} Информация об IP                  ║
║ {GREEN}[4]{WHITE} Проверка Email                    ║
║ {GREEN}[5]{WHITE} OSINT по номеру                   ║
║ {GREEN}[6]{WHITE} Сохранить отчёт                   ║
║ {GREEN}[7]{WHITE} Открыть ссылку в браузере         ║
║ {GREEN}[8]{WHITE} Выход                             ║
╚══════════════════════════════════════╝
""")


def main():
    loading()

    while True:
        menu()
        choice = input(f"{CYAN}╭─[{WHITE}0SINT{CYAN}]\n╰─> {RESET}").strip()

        if choice == "1":
            check_username(ask("Введите username: "))
            pause()

        elif choice == "2":
            get_domain_info(ask("Введите домен: "))
            pause()

        elif choice == "3":
            ip_lookup(ask("Введите IP: "))
            pause()

        elif choice == "4":
            email_lookup(ask("Введите Email: "))
            pause()

        elif choice == "5":
            phone_lookup(ask("Введите номер в международном формате (+380...): "))
            pause()

        elif choice == "6":
            save_report()
            pause()

        elif choice == "7":
            url = ask("Введите URL: ")
            if re.match(r"^https?://", url, re.I):
                open_url(url)
            else:
                print(f"{RED}[!] Нужен URL с http:// или https://{RESET}")
            pause()

        elif choice == "8":
            print(f"{RED}Выход...{RESET}")
            break

        else:
            print(f"{RED}[!] Неверный выбор.{RESET}")
            time.sleep(0.8)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Остановлено пользователем.{RESET}")
