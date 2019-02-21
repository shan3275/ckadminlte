procID=`ps -aux |grep "python cookie.py 8000" |grep -v grep`
if [ "" == "$procID" ];
then
	cd /var/zb
	nohup python cookie.py 8000 &
fi

procID=`ps -aux |grep "python cookie.py 8001" |grep -v grep`
if [ "" == "$procID" ];
then
	cd /var/zb
	nohup python cookie.py 8001 &
fi

procID=`ps -aux |grep "python cookie.py 8002" |grep -v grep`
if [ "" == "$procID" ];
then
	cd /var/zb
	nohup python cookie.py 8002 &
fi

procID=`ps -aux |grep "python cookie.py 8003" |grep -v grep`
if [ "" == "$procID" ];
then
	cd /var/zb
	nohup python cookie.py 8003 &
fi

procID=`ps -aux |grep "python cookie.py 8004" |grep -v grep`
if [ "" == "$procID" ];
then
	cd /var/zb
	nohup python cookie.py 8004 &
fi
