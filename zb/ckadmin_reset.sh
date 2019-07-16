procID=`pstree -ap|grep gunicorn |grep -v grep|head -n 1|awk '{print $1}'|awk -F ',' '{print $2}'`
if [ "" != "$procID" ];
then
	cd /var/v3
	date >> reboot.log
	echo '重启ckadmin' >> reboot.log
	#kill  -HUP $procID
	echo $procID >> reboot.log
	kill  -9 $procID
	sleep 1
	gunicorn -c gunicorn.py app:app &
fi