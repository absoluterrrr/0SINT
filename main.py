import requests
import socket
import whois
import phonenumbers
import time
import random

from phonenumbers import carrier, geocoder, timezone

# =========================================================
# COLORS
# =========================================================

RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BOLD = '\033[1m'
RESET = '\033[0m'

# =========================================================
# CLEAR
# =========================================================

def clear():
    print("\n" * 100)

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

{CYAN}            OSINT TOOL v4
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{GREEN} Creator : Niekocham
{GREEN} Python  : 3.x
{GREEN} Status  : ONLINE
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{RESET}
""")

# =========================================================
# LOADING
# =========================================================

def loading():

    print(f"{YELLOW}Загрузка модулей", end="")

    for i in range(5):

        time.sleep(0.3)
        print(".", end="", flush=True)

    print(f"\n{GREEN}[ OK ] Все модули загружены{RESET}")
    time.sleep(1)

# =========================================================
# USERNAME SEARCH
# =========================================================

def check_username(username):

    print(f"\n{BLUE}=== Поиск аккаунтов: {username} ==={RESET}\n")

    social_media = {

        # =========================================
        # ОСНОВНЫЕ СОЦСЕТИ
        # =========================================

        "Instagram":
            f"https://www.instagram.com/{username}/",

        "Facebook":
            f"https://www.facebook.com/{username}",

        "Twitter/X":
            f"https://x.com/{username}",

        "Threads":
            f"https://www.threads.net/@{username}",

        "TikTok":
            f"https://www.tiktok.com/@{username}",

        "Snapchat":
            f"https://www.snapchat.com/add/{username}",

        "Pinterest":
            f"https://www.pinterest.com/{username}/",

        "LinkedIn":
            f"https://www.linkedin.com/in/{username}/",

        "Tumblr":
            f"https://{username}.tumblr.com",

        "VK":
            f"https://vk.com/{username}",

        "OK.ru":
            f"https://ok.ru/{username}",

        "Quora":
            f"https://www.quora.com/profile/{username}",

        "Medium":
            f"https://medium.com/@{username}",

        "Patreon":
            f"https://www.patreon.com/{username}",

        "OnlyFans":
            f"https://onlyfans.com/{username}",

        "Fansly":
            f"https://fansly.com/{username}",

        # =========================================
        # МЕССЕНДЖЕРЫ
        # =========================================

        "Telegram":
            f"https://t.me/{username}",

        "WhatsApp":
            f"https://wa.me/{username}",

        "Skype":
            f"https://join.skype.com/invite/{username}",

        "Discord":
            f"https://discord.com/users/{username}",

        "Viber":
            f"https://invite.viber.com/{username}",

        # =========================================
        # DEV / PROGRAMMING
        # =========================================

        "GitHub":
            f"https://github.com/{username}",

        "GitLab":
            f"https://gitlab.com/{username}",

        "Bitbucket":
            f"https://bitbucket.org/{username}",

        "Replit":
            f"https://replit.com/@{username}",

        "CodePen":
            f"https://codepen.io/{username}",

        "HackerRank":
            f"https://www.hackerrank.com/{username}",

        "LeetCode":
            f"https://leetcode.com/{username}/",

        # =========================================
        # ВИДЕО / СТРИМЫ
        # =========================================

        "YouTube":
            f"https://www.youtube.com/@{username}",

        "Twitch":
            f"https://www.twitch.tv/{username}",

        "Kick":
            f"https://kick.com/{username}",

        "Trovo":
            f"https://trovo.live/{username}",

        "Vimeo":
            f"https://vimeo.com/{username}",

        "Dailymotion":
            f"https://www.dailymotion.com/{username}",

        # =========================================
        # МУЗЫКА
        # =========================================

        "Spotify":
            f"https://open.spotify.com/user/{username}",

        "SoundCloud":
            f"https://soundcloud.com/{username}",

        "Deezer":
            f"https://www.deezer.com/en/user/{username}",

        "Bandcamp":
            f"https://bandcamp.com/{username}",

        # =========================================
        # ИГРЫ
        # =========================================

        "Steam":
            f"https://steamcommunity.com/id/{username}",

        "Roblox":
            f"https://www.roblox.com/user.aspx?username={username}",

        "Minecraft":
            f"https://namemc.com/profile/{username}",

        "Fortnite":
            f"https://fortnitetracker.com/profile/all/{username}",

        "Xbox":
            f"https://account.xbox.com/en-us/profile?gamertag={username}",

        "PSN":
            f"https://psnprofiles.com/{username}",

        "Chess":
            f"https://www.chess.com/member/{username}",

        # =========================================
        # ФОРУМЫ / COMMUNITY
        # =========================================

        "Reddit":
            f"https://www.reddit.com/user/{username}",

        "4PDA":
            f"https://4pda.to/forum/index.php?showuser={username}",

        "Kaggle":
            f"https://www.kaggle.com/{username}",

        "Pastebin":
            f"https://pastebin.com/u/{username}",

        # =========================================
        # ПРОЧЕЕ
        # =========================================

        "Linktree":
            f"https://linktr.ee/{username}",

        "About.me":
            f"https://about.me/{username}",

        "Behance":
            f"https://www.behance.net/{username}",

        "Dribbble":
            f"https://dribbble.com/{username}",

        "Flickr":
            f"https://www.flickr.com/people/{username}",

        "Gravatar":
            f"https://gravatar.com/{username}",

        "Archive":
            f"https://archive.org/details/@{username}",

        "ProductHunt":
            f"https://www.producthunt.com/@{username}",

        "Tripadvisor":
            f"https://www.tripadvisor.com/members/{username}",

        "DockerHub":
            f"https://hub.docker.com/u/{username}",

        "Keybase":
            f"https://keybase.io/{username}",

        "Taringa":
            f"https://www.taringa.net/{username}",

        "Flipboard":
            f"https://flipboard.com/@{username}",

        "BuyMeACoffee":
            f"https://buymeacoffee.com/{username}",

        "Ko-fi":
            f"https://ko-fi.com/{username}",

        "PornHub":
            f"https://www.pornhub.com/users/{username}",

        "XVideos":
            f"https://www.xvideos.com/profiles/{username}",

        "DEV Community":
            f"https://dev.to/{username}",

        "HackTheBox":
            f"https://app.hackthebox.com/profile/{username}",

        "TryHackMe":
            f"https://tryhackme.com/p/{username}",

        "NexusMods":
            f"https://next.nexusmods.com/profile/{username}",

        "AniList":
            f"https://anilist.co/user/{username}",

        "MyAnimeList":
            f"https://myanimelist.net/profile/{username}",

        "Letterboxd":
            f"https://letterboxd.com/{username}",

        "Goodreads":
            f"https://www.goodreads.com/{username}",

        "Unsplash":
            f"https://unsplash.com/@{username}",

        "500px":
            f"https://500px.com/p/{username}",

        "Freelancer":
            f"https://www.freelancer.com/u/{username}",

        "Fiverr":
            f"https://www.fiverr.com/{username}",

        "Upwork":
            f"https://www.upwork.com/freelancers/{username}",
    }

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    for platform, url in social_media.items():

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=7
            )

            time.sleep(random.uniform(0.5, 1.5))

            if response.status_code == 200:

                print(f"{GREEN}[+] {platform}")
                print(f"{WHITE} ↳ {url}\n")

            elif response.status_code == 404:

                print(f"{RED}[-] {platform}: не найден")

            elif response.status_code == 403:

                print(f"{YELLOW}[!] {platform}: защита сайта")

            else:

                print(f"{YELLOW}[!] {platform}: код {response.status_code}")

        except:

            print(f"{RED}[!] {platform}: ошибка подключения")

# =========================================================
# IP LOOKUP
# =========================================================

def ip_lookup(ip):

    print(f"\n{BLUE}=== Геолокация IP: {ip} ==={RESET}\n")

    try:

        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        if data["status"] == "success":

            print(f"{GREEN}[+] Страна: {data['country']}")
            print(f"{GREEN}[+] Город: {data['city']}")
            print(f"{GREEN}[+] Провайдер: {data['isp']}")
            print(f"{GREEN}[+] Координаты: {data['lat']}, {data['lon']}")
            print(f"{GREEN}[+] Часовой пояс: {data['timezone']}")

        else:

            print(f"{RED}[-] IP не найден")

    except Exception as e:

        print(f"{RED}[!] Ошибка: {e}")

# =========================================================
# EMAIL CHECK
# =========================================================

def email_lookup(email):

    print(f"\n{BLUE}=== Проверка Email: {email} ==={RESET}\n")

    try:

        url = f"https://haveibeenpwned.com/unifiedsearch/{email}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:

            data = response.json()

            print(f"{GREEN}[+] Email найден в утечках\n")

            if "Breaches" in data:

                for breach in data["Breaches"]:

                    print(f"{YELLOW} -> {breach['Name']}")

        else:

            print(f"{RED}[-] Утечки не найдены")

    except Exception as e:

        print(f"{RED}[!] Ошибка: {e}")

# =========================================================
# PHONE OSINT
# =========================================================

def phone_lookup(phone):

    print(f"""{CYAN}

╔══════════════════════════════╗
║      PHONE OSINT INFO        ║
╚══════════════════════════════╝
{RESET}
""")

    try:

        parsed = phonenumbers.parse(phone)

        if not phonenumbers.is_valid_number(parsed):

            print(f"{RED}[-] Номер невалиден")
            return

        country = geocoder.description_for_number(parsed, "ru")
        sim = carrier.name_for_number(parsed, "ru")
        zones = timezone.time_zones_for_number(parsed)

        print(f"{GREEN}[+] Номер валиден")
        print(f"{GREEN}[+] Регион: {country}")
        print(f"{GREEN}[+] Оператор: {sim}")
        print(f"{GREEN}[+] Timezone: {', '.join(zones)}")

        clear_phone = phone.replace("+", "").replace(" ", "")

        print(f"""{CYAN}

╔══════════════════════════════╗
║      POSSIBLE ACCOUNTS       ║
╚══════════════════════════════╝
""")

        accounts = {

            "Telegram":
            f"https://t.me/{clear_phone}",

            "WhatsApp":
            f"https://wa.me/{clear_phone}",

            "Google":
            f"https://www.google.com/search?q={clear_phone}",

            "VK":
            f"https://vk.com/search?c[q]={clear_phone}&c[section]=auto",

            "TrueCaller":
            f"https://www.truecaller.com/search",

            "Sync.me":
            "https://sync.me/",

            "Eyecon":
            "https://eyecon-app.com/"
        }

        for name, url in accounts.items():

            print(f"{GREEN}[+] {name}")
            print(f"{WHITE} ↳ {url}\n")

    except Exception as e:

        print(f"{RED}[!] Ошибка: {e}")

# =========================================================
# DOMAIN INFO
# =========================================================

def get_domain_info(domain):

    print(f"\n{BLUE}=== Домен: {domain} ==={RESET}\n")

    try:

        ip_address = socket.gethostbyname(domain)

        print(f"{GREEN}[+] IP: {ip_address}")

        ip_lookup(ip_address)

    except:

        print(f"{RED}[-] Не удалось получить IP")

    try:

        info = whois.whois(domain)

        print(f"\n{CYAN}[WHOIS]")
        print(f"Домен: {info.domain_name}")
        print(f"Регистратор: {info.registrar}")
        print(f"Создан: {info.creation_date}")
        print(f"Истекает: {info.expiration_date}")

    except Exception as e:

        print(f"{RED}[!] WHOIS ошибка: {e}")

# =========================================================
# MENU
# =========================================================

def menu():

    banner()

    print(f"""
{WHITE}╔══════════════════════════════════╗
{WHITE}║          {CYAN}{BOLD}ГЛАВНОЕ МЕНЮ{WHITE}            ║
{WHITE}╠══════════════════════════════════╣
{WHITE}║ {GREEN}[1]{WHITE}{BOLD}Поиск юзернейма               ║
{WHITE}║ {GREEN}[2]{WHITE}{BOLD}Информация о домене           ║
{WHITE}║ {GREEN}[3]{WHITE}{BOLD}Геолокация IP                 ║
{WHITE}║ {GREEN}[4]{WHITE}{BOLD}Проверка Email                ║
{WHITE}║ {GREEN}[5]{WHITE}{BOLD}OSINT по номеру               ║
{WHITE}║ {GREEN}[6]{WHITE}{BOLD}Выход                         ║
{WHITE}╚══════════════════════════════════╝
""")

# =========================================================
# START
# =========================================================

loading()

while True:
    menu()

    choice = input(f"{CYAN}╭─[{WHITE}OSINT{CYAN}]\n╰─> {RESET}")

    if choice == "1":

        username = input(f"{YELLOW}Введите юзернейм: {RESET}")
        check_username(username)

    elif choice == "2":

        domain = input(f"{YELLOW}Введите домен: {RESET}")
        get_domain_info(domain)

    elif choice == "3":

        ip = input(f"{YELLOW}Введите IP: {RESET}")
        ip_lookup(ip)

    elif choice == "4":

        email = input(f"{YELLOW}Введите Email: {RESET}")
        email_lookup(email)

    elif choice == "5":

        phone = input(f"{YELLOW}Введите номер: {RESET}")
        phone_lookup(phone)

    elif choice == "6":

        print(f"{RED}Выход...")
        break

    else:

        print(f"{RED}Неверный выбор!")

    input(f"\n{CYAN}Нажмите Enter чтобы продолжить...{RESET}")
