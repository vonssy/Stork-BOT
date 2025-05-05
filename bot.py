from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Stork:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        }
        self.GOTRUE_API_URL = "https://app-auth.jp.stork-oracle.network"
        self.STORK_API_URL = "https://app-api.jp.stork-oracle.network"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Stork - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def user_login(self, email: str, password: str, proxy=None, retries=5):
        url = f"{self.GOTRUE_API_URL}/token?grant_type=password"
        data = json.dumps({"email":email, "password":password})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "https://app.stork.network",
            "Referer": "https://app.stork.network/"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(email, proxy, Fore.RED, f"Login Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def refresh_token(self, email: str, password: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.GOTRUE_API_URL}/token?grant_type=refresh_token"
        data = json.dumps({"refresh_token":self.refresh_tokens[email]})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status == 401:
                            await self.process_user_login(email, password, use_proxy)
                            data = json.dumps({"refresh_token":self.refresh_tokens[email]})
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(email, proxy, Fore.RED, f"Refresh Token Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def user_info(self, email: str, proxy=None, retries=5):
        url = f"{self.STORK_API_URL}/v1/me"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result["data"]
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(email, proxy, Fore.RED, f"GET User Data Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def turn_on_verification(self, email: str, proxy=None, retries=5):
        url = f"{self.STORK_API_URL}/v1/stork_signed_prices"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result["data"]
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(email, proxy, Fore.RED, f"GET Message Hash Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
    
    async def validate_verfication(self, email: str, msg_hash: str, proxy=None, retries=5):
        url = f"{self.STORK_API_URL}/v1/stork_signed_prices/validations"
        data = json.dumps({"msg_hash":msg_hash, "valid":True})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://knnliglhgkmlblppdejchidfihjnockl"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(email, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}")
            
    async def process_user_login(self, email: str, password: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        token = None
        while token is None:
            token = await self.user_login(email, password, proxy)
            if not token:
                await asyncio.sleep(5)
                proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                continue

            self.access_tokens[email] = token["access_token"]
            self.refresh_tokens[email] = token["refresh_token"]

            self.print_message(email, proxy, Fore.GREEN, "Login Success")
            return self.access_tokens[email], self.refresh_tokens[email]

    async def process_refreshing_token(self, email: str, password: str, use_proxy: bool):
        while True:
            await asyncio.sleep(55 * 60)

            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            token = None
            while token is None:
                token = await self.refresh_token(email, password, use_proxy, proxy)
                if not token:
                    await asyncio.sleep(5)
                    proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                    continue

                self.access_tokens[email] = token["access_token"]
                self.refresh_tokens[email] = token["refresh_token"]

                self.print_message(email, proxy, Fore.GREEN, "Refresh Token Success")

    async def process_user_earning(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            user = await self.user_info(email, proxy)
            if user:
                verified_msg = user.get("stats", {}).get("stork_signed_prices_valid_count", 0)
                invalid_msg = user.get("stats", {}).get("stork_signed_prices_invalid_count", 0)

                self.print_message(email, proxy, Fore.GREEN,
                    f"Verified Messages:"
                    f"{Fore.WHITE + Style.BRIGHT} {verified_msg} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Invalid Messages: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{invalid_msg}{Style.RESET_ALL}"
                )

            await asyncio.sleep(5 * 60)
            
    async def process_send_ping(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Try to GET Hash Message...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            verify = await self.turn_on_verification(email, proxy)
            if verify:
                for key in verify:
                    if "USD" in key:
                        msg_hash = verify[key].get("timestamped_signature", {}).get("msg_hash")
                        self.print_message(email, proxy, Fore.GREEN, f"Message Hash: {Fore.BLUE+Style.BRIGHT}{self.mask_account(msg_hash)}{Style.RESET_ALL}")

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                ping = await self.validate_verfication(email, msg_hash, proxy)
                if ping and ping.get("message") == "ok":
                    self.print_message(email, proxy, Fore.GREEN, "PING Success")

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 5 Minutes For Next Ping...{Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(5 * 60)
        
    async def process_accounts(self, email: str, password: str, use_proxy: bool):
        self.access_tokens[email], self.refresh_tokens[email] = await self.process_user_login(email, password, use_proxy)
        if self.access_tokens[email] and self.refresh_tokens[email]:
            tasks = [
                asyncio.create_task(self.process_refreshing_token(email, password, use_proxy)),
                asyncio.create_task(self.process_user_earning(email, use_proxy)),
                asyncio.create_task(self.process_send_ping(email, use_proxy))
            ]
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED+Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        email = account["Email"]
                        password = account["Password"]

                        if "@" in email and password:
                            tasks.append(asyncio.create_task(self.process_accounts(email, password, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Stork()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Stork - BOT{Style.RESET_ALL}                                       "                              
        )