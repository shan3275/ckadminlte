procID=`pstree -ap|grep gunicorn |grep -v grep|head -n 1|awk '{print $1}'|awk -F ',' '{print $2}'`
if [ "" != "$procID" ];
then
	cd /var/v3
	date >> reboot.log
	echo '重启ckadmin' >> reboot.log
	kill  -HUP $procID
fi
