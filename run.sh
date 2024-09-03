#!/bin/bash

echo "
╔═╗┬ ┬┌┐ ┬ ┬┬┌─┐┬ ┬
╚═╗│ │├┴┐│││││  ├─┤
╚═╝└─┘└─┘└┴┘┴└─┘┴ ┴ "

url=$1

if [ ! -d "$url" ];then
        mkdir $url
fi

if [ ! -d "$url/recon" ];then
        mkdir $url/recon
fi


echo "[+] Harvesting subdomains with sublist3r..."
sudo sublist3r -d $url >> $url/subs1.txt
cat $url/subs1.txt | grep $1 >> $url/final.txt
rm $url/subs1.txt

echo "[+] Checking for more subdomains with assetfinder..."
sudo assetfinder $url >> $url/subs2.txt
cat $url/subs2.txt | grep $1 >> $url/final.txt
rm $url/subs2.txt

echo "[+] Checking for even more subdomains with amass..."
echo "[+] This may take some time..."
sudo amass enum -d $url >> $url/subs3.txt
cat $url/subs2.txt | grep $1 >> $url/final.txt
rm $url/subs3.txt

echo "[+] Probing for alive domains with httpx..."
cat $url/final.txt | httpx -sc -td -ip >> $url/alive.txt


echo "[+] Checking for possible subdomain takeover..."
 
if [ ! -f "$url/potential_takeovers.txt" ];then
        touch $url/recon/potential_takeovers.txt
fi
 
subjack -w $url/final.txt -t 100 -timeout 30 -ssl -c ~/go/src/github.com/haccer/subjack/fingerprints.json -v 3 -o $url/potential_takeovers.txt
