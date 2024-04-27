#!/bin/sh /etc/rc.common

START=99
STOP=01

USE_PROCD=1

PROG_PATH="/storage/logknockd"
PROG="/usr/bin/python -u -m logknockd"
PIDFILE="/var/run/logknockd.pid"

start_service() {
	procd_open_instance
        procd_set_param env PYTHONPATH=$PROG_PATH
	procd_set_param command $PROG
        procd_set_param respawn ${respawn_threshold:-3600} ${respawn_timeout:-5} ${respawn_retry:-5}
	procd_set_param stdout 1
        procd_set_param stderr 1
        procd_set_param pidfile $PIDFILE
	procd_close_instance
}
