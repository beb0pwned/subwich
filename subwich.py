#TODO: Add important IPs flag that checks for IPs with unique services running ex. sql etc.:::: Add cider notation checker for amass
import re
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

def wayback(domain):
    create_dir(f"{domain}/wayback")
    create_dir(f"{domain}/wayback/extensions")

    print(f"{BOLD_TEAL}[+] Scraping wayback data...{RESET}")
    wayback_output = run_command(f"cat {domain}/final.txt | waybackurls")
    with open(f"{domain}/wayback/wayback.txt", 'w') as f:
        f.write(wayback_output)

    print(f"[+] Extracting parameters from wayback data...")
    wayback_params = run_command(f"cat {domain}/wayback/wayback.txt | grep '?*=' | cut -d '=' -f 1 | sort -u")
    with open(f"{domain}/wayback/wayback_params.txt", 'w') as f:
        for line in wayback_params.splitlines():
            f.write(line + '=\n')

    print(f"[+] Extracting files with specific extensions...")
    with open(f"{domain}/wayback/wayback.txt", 'r') as wayback_file:
        for line in wayback_file:
            line = line.strip()
            ext = line.split('.')[-1]
            if ext in ['js', 'html', 'json', 'php', 'aspx']:
                with open(f"{domain}/wayback/extensions/{ext}.txt", 'a') as ext_file:
                    ext_file.write(line + '\n')

def nmap_scan(domain):
    create_dir(f"{domain}/nmap")
    print(f"{BOLD_TEAL}[+] Scanning for open ports using Nmap...{RESET}")
    run_command(f"nmap -oA {domain}/nmap/nmap -iL {domain}/ips.txt -T4 ")

def format_amass(input_file, output_file, output_file_2):
    with open(input_file, "r") as infile, open(output_file, "a") as outfile, open(output_file_2, "a") as outfile_2:
        pattern_domain_ip = re.compile(r'(\S+\.ch).*?(\d{1,3}(?:\.\d{1,3}){3})')
        pattern_domain_only = re.compile(r'(\S+\.ch)')

        for line in infile:
            match_domain_ip = pattern_domain_ip.search(line)
            if match_domain_ip:
                domain = match_domain_ip.group(1)
                ip = match_domain_ip.group(2)
                outfile.write(f"{domain}\n")
                outfile_2.write(f"{ip}\n")
                continue
            match_domain_only = pattern_domain_only.findall(line)
            if match_domain_only:
                for domain in match_domain_only:
                    outfile.write(f"{domain}\n")

def main():
    try:
        # Check if the script is being run with sudo privs
        if os.getuid() != 0:
            print(f'{BOLD_RED}Please use sudo.{RESET}')

        parser = argparse.ArgumentParser(description="Domain Enumeration and Recon Tool")
        parser.add_argument("-d", "--domain", help="Target domain")
        parser.add_argument("-w", action='store_true', help="Enable scraping WaybackURLs. MUST BE USED WITH -d")
        parser.add_argument("-isubs", help="Extract subdomains from a list that contain test, dev, admin, etc...")
        parser.add_argument("-skip-amass", action='store_true', help="Skips scanning for subdomains with amass")
        parser.add_argument("-nmap", action="store_true", help="Enables basic nmap scan. ie -oA -T4 -iL. MUST BE USED WITH -d")
        args = parser.parse_args()

        
        if args.domain:
            banner()
            domain = args.domain

            create_dir(domain)
            if (args.w or args.nmap) and os.path.exists(f'{domain}/final.txt'):
                print(f"{BOLD_ORANGE}[!] Skipping subdomain scans -> Scans already ran on this domain.{RESET}")

            else:  
                print(f"{BOLD_TEAL}[+] Harvesting subdomains for {domain} with subfinder...{RESET}")
                subfinder_output = run_command(f"subfinder -d {domain} -v")
                with open(f"{domain}/final.txt", 'w') as f:
                    f.write(subfinder_output)

                print(f"{BOLD_TEAL}[+] Checking for more subdomains with assetfinder...{RESET}")
                assetfinder_output = run_command(f"assetfinder {domain}")
                with open(f"{domain}/final.txt", 'a') as f:
                    f.write(assetfinder_output)

                if not args.skip_amass:
                    print(f"{BOLD_TEAL}[+] Checking for even more subdomains with amass...{RESET}")
                    amass_output = run_command(f"amass enum -d {domain} -timeout 60 -nf {domain}/final.txt -o {domain}/amass.txt")
                    format_amass(input_file=f"{domain}/amass.txt",output_file=f"{domain}/final.txt",output_file_2=f"{domain}/ips.txt")
                    
                else:
                    print(f"{BOLD_ORANGE}[!] Skipping Amass subdomain scan.{RESET}")


                print(f"{BOLD_MAGENTA}[+] Probing for alive domains with httpx...{RESET}")
                httpx_output = run_command(f"cat {domain}/final.txt | httpx -sc -td -ip")
                with open(f"{domain}/alive.txt", 'w') as f:
                    f.write(httpx_output)

                # Extract IPs and domains from httpx output
                with open(f"{domain}/ips.txt", 'w') as ip_file:
                    ips = run_command(f"cat {domain}/alive.txt | grep -oE '\\b([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}\\b'")
                    ip_file.write(ips)

                with open(f"{domain}/domains_alive.txt", 'w') as domain_file:
                    domains = run_command(f"cat {domain}/alive.txt | sed 's|https\\?://\\([^ ]*\\).*|\\1|'")
                    domain_file.write(domains)

                print(f"{BOLD_MAGENTA}[+] Checking for possible subdomain takeover...{RESET}")
                run_command(f"subjack -w {domain}/final.txt -t 100 -timeout 30 -ssl -c 'subjack_fingerprints.json' -v 3 > {domain}/potential_takeovers.txt")
                
            if args.w:
                wayback(domain=domain)
                print(f"{BOLD_ORANGE}[+] WaybackURLs scan complete.{RESET}")
                
            if args.nmap:
                nmap_scan(domain=domain)
                print(f"{BOLD_ORANGE}[+] Nmap scan complete.{RESET}")

            print(f"{BOLD_ORANGE}[+] Reconnaissance complete.{RESET}")


        # Check for important subdoamins in a .txt file
        elif args.isubs:
            important_keywords = [
                        "admin", "dev", "test", "api", "staging", "prod", "beta", "manage", "jira",
                        "github", "panel", "dashboard", "secure", "alpha", "demo", "sandbox", 
                        "auth", "login", "git", "monitor", "logs", "billing", "db", "internal"
                    ]

            print(f"{GREEN}Scanning for important subdomains...{RESET}")

            with open(f"{args.isubs}", "r") as f:
                important_subs = []
                subdomains = [x.strip() for x in f.readlines()]

                for subdomain in subdomains:
                    if any(keyword in subdomain for keyword in important_keywords):
                        important_subs.append(subdomain)

                for pos, value in enumerate(important_subs):
                    print(f"{TEAL}{pos}: {GREEN}{value}")
                with open(f"isubs.txt", "w") as f:
                    for goodsubs in important_subs:
                        f.writelines(f"{goodsubs}\n")

        else:
            banner()
            parser.print_help()


    except KeyboardInterrupt:
        print(f'\n{BOLD_RED}Installation interrupted by user.{RESET}')

    except Exception as e:
        print(f'{RED}An error occured: {e}{RESET}')
        
if __name__ == "__main__":
    main()
