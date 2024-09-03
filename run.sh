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
sudo amass enum -d $url >> $url/subs3.txt
cat $url/subs2.txt | grep $1 >> $url/final.txt
rm $url/subs3.txt

echo "[+] Probing for alive domains with httpx..."
cat $url/final.txt | httpx -sc -td -ip >> $url/alive.txt

