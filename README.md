# ![image](https://github.com/user-attachments/assets/95867237-f92b-464d-a70b-bae0abbb3cf7)
Subdomain enumeration tool

## About
Automate recon for bug bounties
- Note: Please ensure that Go is properly installed on your system for this tool to function correctly.

## Requirements
- snap
- go

## Installation
- `python3 install.py`

## Example Usage
Note: Must be in the format of "domain.com" or "this.domain.com" etc.. DO NOT add the protocol ex. https://domain.com
- `python3 subwich.py <domain>`
- `-w` will enable waybackurls to scrape ex. `python3 subwich.py <domain> -w`
- `-isubs` will check for important subdomains in a txt file ex. `python3 subwich.py -isubs alive.txt`
- `-skip-amass` will skip amass subdomain search as amass can take a while, especially on complex domains ex. `python3 subwich.py -d domain.com -skip-amass

