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

banner = f"""{RED}
╔═╗┬ ┬┌┐ ┬ ┬┬┌─┐┬ ┬
╚═╗│ │├┴┐│││││  ├─┤
╚═╝└─┘└─┘└┴┘┴└─┘┴ ┴ {RESET}
                    V2.0
{TEAL}by beb0pwned{RESET}
"""

def help():
    print(banner)
    print("\nUsage python3 subwich.py -u <domain>")
    print("\nOptions:")
    print("  -u, --url <domain>  Specify the target domain")
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
        print(f"Error executing command: {e}")
        return ""

def main():
    parser = argparse.ArgumentParser(description="Domain Enumeration and Recon Tool")
    parser.add_argument("-u", "--url", help="Target domain")
    parser.add_argument("-w", action='store_true', help="Scrape WaybackURLs")
    args = parser.parse_args()

    # Display help if no domain is provided or -h flag is used
    if args.h or not args.url:
        help()
        sys.exit(1)

    banner()
    url = args.url

    # Create necessary directories
    create_dir(url)
    create_dir(f"{url}/wayback")
    create_dir(f"{url}/wayback/extensions")

    print(f"[+] Harvesting subdomains for {url} with subfinder...")
    subfinder_output = run_command(f"sudo subfinder -d {url}")
    with open(f"{url}/final.txt", 'w') as f:
        f.write(subfinder_output)

    print("[+] Checking for more subdomains with assetfinder...")
    assetfinder_output = run_command(f"sudo assetfinder {url}")
    with open(f"{url}/final.txt", 'a') as f:
        f.write(assetfinder_output)

    print("[+] Checking for even more subdomains with amass...")
    amass_output = run_command(f"sudo amass enum -d {url}")
    with open(f"{url}/final.txt", 'a') as f:
        f.write(amass_output)

    print("[+] Probing for alive domains with httpx...")
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

    print("[+] Checking for possible subdomain takeover...")
    run_command(f"subjack -w {url}/final.txt -t 100 -timeout 30 -ssl -c /usr/share/subjack/fingerprints.json -v 3 > {url}/potential_takeovers.txt")

    if args.w:
        print("[+] Scraping wayback data...")
        wayback_output = run_command(f"cat {url}/final.txt | waybackurls")
        with open(f"{url}/wayback/wayback.txt", 'w') as f:
            f.write(wayback_output)

        print("[+] Extracting parameters from wayback data...")
        wayback_params = run_command(f"cat {url}/wayback/wayback.txt | grep '?*=' | cut -d '=' -f 1 | sort -u")
        with open(f"{url}/wayback/wayback_params.txt", 'w') as f:
            for line in wayback_params.splitlines():
                f.write(line + '=\n')

        print("[+] Extracting files with specific extensions...")
        with open(f"{url}/wayback/wayback.txt", 'r') as wayback_file:
            for line in wayback_file:
                line = line.strip()
                ext = line.split('.')[-1]
                if ext in ['js', 'html', 'json', 'php', 'aspx']:
                    with open(f"{url}/wayback/extensions/{ext}.txt", 'a') as ext_file:
                        ext_file.write(line + '\n')

    print("[+] Scanning for open ports using Nmap...")
    run_command(f"nmap -iL {url}/ips.txt -T4 -oA {url}/nmap")

    print("\n[+] Reconnaissance complete!")

if __name__ == "__main__":
    main()
