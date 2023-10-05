crontab -l > cron.txt
cat croncommand.txt >> cron.txt
crontab cron.txt
rm cron.txt