#TODO: make look nicer
import os
import subprocess

GREEN = "\033[92m"
MAGENTA = "\033[95m"
BOLD_GREEN = "\033[1;92m"
BOLD_RED = "\033[1;91m"
BOLD_ORANGE = "\033[1;93m"
RESET = "\033[0m"

prerequisites = [
    'libpcap-dev',
    'linux-headers-generic',
]

tools = [
    'nmap',
    'snapd'
]

snap_tools = [
    'amass',
]

go_tools = [
    ['httpx','github.com/projectdiscovery/httpx/cmd/httpx@latest'],
    ['subfinder','github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'],
    ['assetfinder', 'github.com/tomnomnom/assetfinder@latest'],
    ['subjack', 'github.com/haccer/subjack@latest'],
    ['waybackurls', 'github.com/tomnomnom/waybackurls@latest']
]  

def install_tools():
    # Update + Upgrade first
    print(f"\n{BOLD_GREEN}Updating and Upgrading...{RESET}\n")
    os.system("apt update -y && apt upgrade -y && apt full-upgrade -y")

    # Install Prerequisites
    print(f'\n{BOLD_GREEN}Installing prerequisites...{RESET}\n')
    for prereq in prerequisites:
        print(f'{GREEN}Installing {prereq}...{RESET}')
        os.system(f'apt install {prereq} -y')

    #Install tools
    print(f"\n{BOLD_GREEN}Starting installation...\n{RESET}")
    for tool in tools:
        print(f"{GREEN}Installing {tool}{RESET}")
        os.system(f'apt install {tool} -y')

    # Install snap tools
    for tool in snap_tools:
        print(f"{GREEN}Installing {tool} with snap.{RESET}")
        os.system(f'snap install {tool}')

    # Download tools that need Go to download
    print(f"\n{BOLD_GREEN}Installing tools using go...{RESET}\n")
    for tool in go_tools:
        tool_name = tool[0]
        download_url  = tool[1]

        print(f'{MAGENTA}Installing {tool_name}...{RESET}')
        result = subprocess.run(
            ['go', 'install', '-v', download_url],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f'{GREEN}{tool_name} downloaded successfully.{RESET}\n')
        else:
            print(f'{BOLD_RED}Failed to download {tool_name}: {result.stderr}{RESET}\n')

def main():
    try:
        install_tools()
        print(f'{BOLD_ORANGE}Installtion complete.{RESET}')
    except KeyboardInterrupt:
        print(f'{BOLD_RED}User stopped installation.\n\nExitting...{RESET}')
    except Exception as e:
        print(f'\n{BOLD_RED}Error:{RESET} {e}')


if __name__ == "__main__":
    main()
