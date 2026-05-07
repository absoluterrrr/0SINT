import requests
import socket
import whois
import keyboard
import requests
# Цвета
RED    = '\033[31m'
GREEN  = '\033[32m'
YELLOW = '\033[33m'
BLUE   = '\033[34m'
MAGENTA = '\033[35m'
CYAN   = '\033[36m'
WHITE  = '\033[37m'
print(f"{WHITE}\033[1mНапишите отзыв в телеграм, создателю, если есть желания. \n\033[1m––– Niekocham ––– ")
a = input("Введите Enter чтобы начать: ")
BOLD   = '\033[1m'
UNDERLINE = '\033[4m'
RESET  = '\033[0m'

 
def check_username(username):
    print(f"{WHITE}\n--- Поиск аккаунтов по: {username} ---")
    social_media = {
        "Instagram": f"https://www.instagram.com/{username}/",
        "Twitter": f"https://twitter.com/user/{username}",
        "GitHub": f"https://github.com/{username}",
        "Telegram": f"https://t.me/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Youtube": f"https://www.youtube.com/{username}",
        "Megogo": f"https://megogo.net/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "WordPress": f"https://www.wordpress.com/user/{username}",
        "Vimeo": f"https://www.vimeo.com/{username}",
        "Tiktok": f"https://www.tiktok.com/@{username}",
        "Archive": f"https://archive.org/{username}",
        "WHATSAPP": f"https://wa.me/{username}",
        "Viber":f"://https://www.viber.com/",
        
        
        
    }

    
    for platform, url in social_media.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"[+] {platform}: {url}")
            elif response.status_code == 404:
                print(f"[-] {platform}: Не найден")
            else:
                print(f"[!] {platform}: Ошибка {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"[!] {platform}: Ошибка соединения")

def get_domain_info(domain):
    print(f"{WHITE}{BOLD}\n--- Инфраструктура домена: {domain} ---")
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"[+] IP-адрес: {ip_address}")
    except socket.gaierror:
        print("[-] Не удалось получить IP-адрес.")

if __name__ == "__main__":
    choice = input(f"{WHITE}{BOLD}Что ищем? (1 - Юзернейм, 2 - Домен) ")

    if choice == '1':
        name = input("Введите юзернейм: ")
        check_username(name)
    if choice == '2':
        target_domain = input("Введите домен (например, google.com): ")
        
        get_domain_info(target_domain)
        response = requests.get(f"https://dns.google/resolve?name={target_domain}&type=A") 
        # Parse the JSON response 
        data = response.json()    
        print(data)
        
else:
    print("Неверный выбор.")



