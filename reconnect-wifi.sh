#!/usr/bin/env bash
# reconnect wifi when it drops

#set -x

NetCard=wlan0	 		        # the netcard connected to the internet
PingTarget=192.168.1.1          # the ping target, router ip or website, etc: 192.168.1.1, www.baidu.com
LogFile=~john/reconnect-wifi.log	# log file
LogAll=false			        # log msg no matter whether the net is connected, used to be check whether the script is running.

test -e $LogFile || touch $LogFile

time=$(date "+%Y/%m/%d %H:%M:%S")

ret=$(ping -c 2 -W 1 -I $NetCard $PingTarget | grep 'received' | cut -d ',' -f 2 | cut -d ' ' -f 2)

if [ "$ret" == "0" ]; then
    ifdown wlan0 && ifup wlan0
    echo "Try Reconnect: $?, $time" | tee -a $LogFile
else
    if [ "$LogAll" == "true" ]; then
        echo "Network is ok, ret = $ret, $time" | tee -a $LogFile
    fi
fi

exit 0
