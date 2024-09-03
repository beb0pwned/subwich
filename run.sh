#!/bin/bash

echo "
╔═╗┬ ┬┌┐ ┬ ┬┬┌─┐┬ ┬
╚═╗│ │├┴┐│││││  ├─┤
╚═╝└─┘└─┘└┴┘┴└─┘┴ ┴ "

url=$1

if [ ! -d "$url" ];then
        mkdir $url
fi

if [! -d "$url/wayback"];then
        mkdir $url/wayback
fi

if [ ! -d "$url/wayback/extensions" ];then
        mkdir $url/wayback/extensions
fi

echo "[+] Harvesting subdomains with subfinder..."
sudo subfinder -d $url >> $url/subs1.txt
cat $url/subs1.txt | grep $1 >> $url/final.txt
rm $url/subs1.txt

echo "[+] Checking for more subdomains with assetfinder..."
sudo assetfinder $url >> $url/subs2.txt
cat $url/subs2.txt | grep $1 >> $url/final.txt
rm $url/subs2.txt

echo "[+] Probing for alive domains with httpx..."
cat $url/final.txt | httpx -sc -td -ip >> $url/alive.txt


echo "[+] Checking for possible subdomain takeover..."

if [ ! -f "$url/potential_takeovers.txt" ];then
        touch $url/potential_takeovers.txt
fi
 
subjack -w $url/final.txt -t 100 -timeout 30 -ssl -c /usr/share/subjack/fingerprints.json -v 3 >> $url/potential_takeovers.txt


echo "[+] Scraping wayback data..."
cat $url/final.txt | waybackurls | tee -a $url/wayback/wayback.txt

echo "[+] Pulling and compiling all params found in wayback data..."
cat $url/wayback/wayback.txt | grep '?*=' | cut -d "=" -f 1 | sort -u >> $url/wayback/wayback_params.txt
for line in $(cat $url/wayback/wayback_params.txt); do echo $line'=';done

echo "[+] Pulling and compiling js/php/aspx/jsp/json files from wayback output..."
for line in $(cat $url/wayback/wayback.txt);do
        ext="${line##*.}"
        if [[ "$ext" == "js" ]]; then
            echo $line | sort -u | tee -a  $url/wayback/extensions/js.txt
        fi
        if [[ "$ext" == "html" ]];then
            echo $line | sort -u | tee -a $url/wayback/extensions/jsp.txt
        fi
        if [[ "$ext" == "json" ]];then
            echo $line | sort -u | tee -a $url/wayback/extensions/json.txt
        fi
        if [[ "$ext" == "php" ]];then
            echo $line | sort -u | tee -a $url/wayback/extensions/php.txt
        fi
        if [[ "$ext" == "aspx" ]];then
            echo $line | sort -u | tee -a $url/wayback/extensions/aspx.txt
        fi
    done


echo "[+] Scanning for open ports using Nmap..."
nmap -iL $url/alive.txt -T4 -oA $url/nmap.txt