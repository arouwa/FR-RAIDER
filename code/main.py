import requests
import time
import random
import os
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor  # Paralel çalıştırma için
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Colorama'yı başlat
init(autoreset=True)

# Token'ları dosyadan yükle
def load_tokens(filename='tokens.txt'):
    with open(filename, 'r') as file:
        tokens = file.read().splitlines()
    return tokens

# Token doğrulama fonksiyonu
def check_tokens(tokens):
    valid_tokens = []
    for token in tokens:
        headers = {
            'Authorization': token
        }
        response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + f"[GEÇERLİ] {token}")
            valid_tokens.append(token)
        else:
            print(Fore.RED + f"[GEÇERSİZ] {token}")
    return valid_tokens



# Mesaj gönderme fonksiyonu
def send_message(token, channel_id, message):
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {
        'content': f"{message}"
    }
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print(Fore.RED + f"Mesaj başarıyla gönderildi, token {token[:10]}...!")
    else:
        print(Fore.RED + f"Mesaj gönderilemedi: {response.status_code} - {response.text}")

# Raid fonksiyonu (şimdi mesajları paralel gönderiyor)
def raid(tokens):
    if not tokens:
        print(Fore.RED + "Token'lar tokens.txt dosyasından yüklenemedi.")
        return

    channel_id = input(Fore.RED + "Kanal ID'si:  ")
    message = input(Fore.RED + "Mesaj:  ")
    num_messages = int(input(Fore.RED + "Mesaj sayısı: "))
    ping_everyone = input(Fore.RED + "Herkese ping atılsın mı? (e/h): ").strip().lower()
    delay_between_messages = float(input(Fore.RED + "Mesajlar arasındaki gecikme (saniye): "))
    
    ping_everyone = '@everyone ' if ping_everyone == 'e' else ''
    
    # Gönderilecek tam mesajı hazırlıyoruz
    full_message = ping_everyone + message

    # ThreadPoolExecutor kullanarak mesajları paralel olarak gönderiyoruz
    with ThreadPoolExecutor() as executor:
        for i in range(num_messages):
            for token in tokens:
                executor.submit(send_message, token, channel_id, full_message)
            time.sleep(delay_between_messages)  # Mesajlar arasında gecikme


def change_nickname(token, guild_id, nickname):
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me"
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {
        'nick': nickname
    }
    response = requests.patch(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print(Fore.GREEN + f"Takma ad başarıyla değiştirildi, token {token[:10]}...")
    else:
        print(Fore.RED + f"Takma ad değiştirilemedi: {response.status_code} - {response.text}")


# Kullanıcı adını değiştirme fonksiyonu
def change_username(token, new_username):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {
        'username': new_username
    }
    response = requests.patch(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print(Fore.GREEN + f"Kullanıcı adı başarıyla değiştirildi, token {token[:10]}...")
    else:
        print(Fore.RED + f"Kullanıcı adı değiştirilemedi: {response.status_code} - {response.text}")

        
# Raid v2 fonksiyonu (mesajlar sırayla gönderiliyor)
def raid_v2(tokens):
    if not tokens:
        print(Fore.RED + "Token'lar tokens.txt dosyasından yüklenemedi.")
        return

    channel_id = input(Fore.RED + "Kanal ID'si:  ")
    message = input(Fore.RED + "Mesaj:  ")
    num_messages = int(input(Fore.RED + "Mesaj sayısı: "))
    ping_everyone = input(Fore.RED + "Herkese ping atılsın mı? (e/h): ").strip().lower()
    delay_between_messages = float(input(Fore.RED + "Mesajlar arasındaki gecikme (saniye): "))
    
    ping_everyone = '@everyone ' if ping_everyone == 'e' else ''
    
    # Gönderilecek tam mesajı hazırlıyoruz
    full_message = ping_everyone + message

    for i in range(num_messages):
        for token in tokens:
            send_message(token, channel_id, full_message)
            time.sleep(delay_between_messages)  # Mesajlar arasında gecikme


# Profil fotoğrafını değiştirme fonksiyonu
def change_pfp(token, pfp_path):
    url = "https://discord.com/api/v9/users/@me/avatar"
    headers = {
        'Authorization': token
    }
    with open(pfp_path, 'rb') as f:
        m = MultipartEncoder(fields={'file': ('pfp.png', f, 'image/png')})
        headers['Content-Type'] = m.content_type
        response = requests.patch(url, data=m, headers=headers)
    
    if response.status_code == 200:
        print(Fore.GREEN + f"Profil fotoğrafı başarıyla değiştirildi, token {token[:10]}...")
    else:
        print(Fore.RED + f"Profil fotoğrafı değiştirilemedi: {response.status_code} - {response.text}")

# Sunucuya katılma fonksiyonu
def join_server(token, invite_code):
    url = f'https://discord.com/api/v9/invites/{invite_code}'
    headers = {
        'Authorization': token
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print(Fore.GREEN + f"Token {token[:10]}... başarıyla sunucuya katıldı!")
    elif response.status_code == 401:
        print(Fore.RED + "401 Yetkisiz: Geçersiz token veya sunucuya katılmak için izin yok.")
    else:
        print(Fore.RED + f"Sunucuya katılamadı: {response.status_code} - {response.text}")

# Rich Presence ayarlama fonksiyonu
def set_rpc(token, activity_name="Bir şeyler oynuyor...", activity_type=0):
    url = "https://discord.com/api/v9/users/@me/settings"
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {
        "custom_status": None,
        "status": "online",
        "activities": [
            {
                "name": activity_name,
                "type": activity_type,  # 0: Oynuyor, 1: Yayın yapıyor, 2: Dinliyor, 3: İzliyor
                "application_id": None,
                "details": "Eğleniyorum!",
                "timestamps": {"start": int(time.time())}
            }
        ]
    }
    response = requests.patch(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print(Fore.GREEN + f"RPC başarıyla ayarlandı, token {token[:10]}...")
    else:
        print(Fore.RED + f"RPC ayarlanamadı: {response.status_code} - {response.text}")

# Ana menü
def main():
    while True:
        # Menü gösterilmeden önce ekranı temizle
        os.system('cls' if os.name == 'nt' else 'clear')

        print(Fore.RED + """
  █████▒██▀███    ██████  ██░ ██  ▒█████   ██▓███  
▓██   ▒▓██ ▒ ██▒▒██    ▒ ▓██░ ██▒▒██▒  ██▒▓██░  ██▒
▒████ ░▓██ ░▄█ ▒░ ▓██▄   ▒██▀▀██░▒██░  ██▒▓██░ ██▓▒
░▓█▒  ░▒██▀▀█▄    ▒   ██▒░▓█ ░██ ▒██   ██░▒██▄█▓▒ ▒
░▒█░   ░██▓ ▒██▒▒██████▒▒░▓█▒░██▓░ ████▓▒░▒██▒ ░  ░
 ▒ ░   ░ ▒▓ ░▒▓░▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒░ ▒░▒░▒░ ▒▓▒░ ░  ░
 ░       ░▒ ░ ▒░░ ░▒  ░ ░ ▒ ░▒░ ░  ░ ▒ ▒░ ░▒ ░     
 ░ ░     ░░   ░ ░  ░  ░   ░  ░░ ░░ ░ ░ ▒  ░░       
          ░           ░   ░  ░  ░    ░ ░           
                                                   

1-) Raid
2-) Raid v2
3-) Mass Join
4-) Set RPC
5-) Check Tokens
6-) Kullanıcı Adını Değiştir
7-) Profil Fotoğrafını Değiştir
8-) Görünür Adı Değiştir
            By Arouwa
        """)
        choice = input("Seçiminizi girin: ")

        tokens = load_tokens()
        if choice == '1':
            raid(tokens)
        elif choice == '2':
            raid_v2(tokens)
        elif choice == '3':
            mass_join(tokens)
        elif choice == '4':
            activity_name = input("Etkinlik adını girin: ")
            activity_type = int(input("Etkinlik türünü seçin (0: Oynuyor, 1: Yayın Yapıyor, 2: Dinliyor, 3: İzliyor): "))
            for token in tokens:
                set_rpc(token, activity_name, activity_type)
            input("Ana menüye dönmek için Enter'a basın...")

        elif choice == '5':
            valid_tokens = check_tokens(tokens)
            print(Fore.GREEN + f"Geçerli token sayısı: {len(valid_tokens)}/{len(tokens)}")
            input("Ana menüye dönmek için Enter'a basın...")
        elif choice == '6':
            new_username = input("Yeni kullanıcı adını girin: ")
            for token in tokens:
                change_username(token, new_username)
        elif choice == '7':
            pfp_path = input("Profil fotoğrafının yolunu girin (örneğin: pfp.png): ")
            for token in tokens:
                change_pfp(token, pfp_path)
        elif choice == '8':
            guild_id = input("Sunucu ID'sini girin: ")
            nickname = input("Yeni görünür adınızı girin: ")
            for token in tokens:
                change_nickname(token, guild_id, nickname)
        else:
            print(Fore.RED + "Geçersiz seçim. Lütfen tekrar deneyin.")
            input("Ana menüye dönmek için Enter'a basın...")

if __name__ == "__main__":
    main()
