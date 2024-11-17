import sys
import os
import subprocess
import argparse


# COLORS
GREEN = "\033[92m"
RED = "\033[91m"
TEAL = "\033[96m"
MAGENTA = "\033[95m"
ORANGE = "\033[93m"
BOLD_ORANGE = "\033[1;93m"
RESET = "\033[0m"
BOLD_GREEN = "\033[1;92m"
BOLD_RED = "\033[1;91m"
BOLD_MAGENTA = "\033[1;95m"
BOLD_TEAL = "\033[1;96m"

def banner():
    print(f"""{RED}
╔═╗┬ ┬┌┐ ┬ ┬┬┌─┐┬ ┬
╚═╗│ │├┴┐│││││  ├─┤
╚═╝└─┘└─┘└┴┘┴└─┘┴ ┴ {RESET}
                    V2.0
{BOLD_MAGENTA}by beb0pwned{RESET}
"""
    )

def help():
    banner()
    print("\nUsage python3 subwich.py -u <domain>")
    print("\nOptions:")
    print("  -d, --domain <domain>  Specify the target domain")
    print("  -w           Scrape WaybackURLs")
    print("  -h           Displays this help message\n")

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{BOLD_RED}Error executing command: {e}{RESET}")
        return ""

def main():
    try:
        parser = argparse.ArgumentParser(description="Domain Enumeration and Recon Tool")
        parser.add_argument("-d", "--domain", help="Target domain")
        parser.add_argument("-w", action='store_true', help="Scrape WaybackURLs")
        args = parser.parse_args()

        # Display help if no domain is provided or -h flag is used
        if not args.domain:
            print(f"\n{BOLD_RED}Please provide a domain.{RESET}")
            help()
            sys.exit(1)

        banner()
        url = args.domain

        # Create necessary directories
        create_dir(url)
        create_dir(f"{url}/wayback")
        create_dir(f"{url}/wayback/extensions")

        print(f"{BOLD_TEAL}[+] Harvesting subdomains for {url} with subfinder...{RESET}")
        subfinder_output = run_command(f"sudo subfinder -d {url}")
        with open(f"{url}/final.txt", 'w') as f:
            f.write(subfinder_output)

        print(f"{BOLD_TEAL}[+] Checking for more subdomains with assetfinder...{RESET}")
        assetfinder_output = run_command(f"sudo assetfinder {url}")
        with open(f"{url}/final.txt", 'a') as f:
            f.write(assetfinder_output)

        print(f"{BOLD_TEAL}[+] Checking for even more subdomains with amass...{RESET}")
        amass_output = run_command(f"sudo amass enum -d {url}")
        with open(f"{url}/final.txt", 'a') as f:
            f.write(amass_output)

        print(f"{BOLD_TEAL}[+] Probing for alive domains with httpx...{RESET}")
        httpx_output = run_command(f"cat {url}/final.txt | httpx -sc -td -ip")
        with open(f"{url}/alive.txt", 'w') as f:
            f.write(httpx_output)

        # Extract IPs and domains from httpx output
        with open(f"{url}/ips.txt", 'w') as ip_file:
            ips = run_command(f"cat {url}/alive.txt | grep -oE '\\b([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}\\b'")
            ip_file.write(ips)

        with open(f"{url}/domains_alive.txt", 'w') as domain_file:
            domains = run_command(f"cat {url}/alive.txt | sed 's|https\\?://\\([^ ]*\\).*|\\1|'")
            domain_file.write(domains)

        print(f"{BOLD_TEAL}[+] Checking for possible subdomain takeover...{RESET}")
        run_command(f"subjack -w {url}/final.txt -t 100 -timeout 30 -ssl -c /usr/share/subjack/fingerprints.json -v 3 > {url}/potential_takeovers.txt")

        if args.w:
            print(f"{BOLD_TEAL}[+] Scraping wayback data...{RESET}")
            wayback_output = run_command(f"cat {url}/final.txt | waybackurls")
            with open(f"{url}/wayback/wayback.txt", 'w') as f:
                f.write(wayback_output)

            print(f"{BOLD_TEAL}[+] Extracting parameters from wayback data...{RESET}")
            wayback_params = run_command(f"cat {url}/wayback/wayback.txt | grep '?*=' | cut -d '=' -f 1 | sort -u")
            with open(f"{url}/wayback/wayback_params.txt", 'w') as f:
                for line in wayback_params.splitlines():
                    f.write(line + '=\n')

            print(f"{BOLD_TEAL}[+] Extracting files with specific extensions...{RESET}")
            with open(f"{url}/wayback/wayback.txt", 'r') as wayback_file:
                for line in wayback_file:
                    line = line.strip()
                    ext = line.split('.')[-1]
                    if ext in ['js', 'html', 'json', 'php', 'aspx']:
                        with open(f"{url}/wayback/extensions/{ext}.txt", 'a') as ext_file:
                            ext_file.write(line + '\n')

        print(f"{BOLD_TEAL}[+] Scanning for open ports using Nmap...{RESET}")
        run_command(f"nmap -iL {url}/ips.txt -T4 -oA {url}/nmap")

        print(f"{BOLD_GREEN}\n[+] Reconnaissance complete!{RESET}")

    except KeyboardInterrupt:
        print(f'\n{BOLD_RED}Installation interrupted by user.{RESET}')

    except Exception as e:
        print(f'{RED}An error occured: {e}{RESET}')
if __name__ == "__main__":
    main()
