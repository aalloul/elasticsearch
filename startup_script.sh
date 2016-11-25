#!/bin/sh
#
# elasticsearch <summary>
#
# chkconfig:   2345 80 20
# description: Starts and stops a single elasticsearch instance on this system
#

### BEGIN INIT INFO
# Provides: Elasticsearch (data)
# Required-Start: $network $named
# Required-Stop: $network $named
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: This service manages the elasticsearch daemon
# Description: Elasticsearch is a very scalable, schema-free and high-performance search solution supporting multi-tenancy and near realtime search.
### END INIT INFO

#
# init.d / servicectl compatibility (openSUSE)
#
if [ -f /etc/rc.status ]; then
    . /etc/rc.status
    rc_reset
fi

#
# Source function library.
#
if [ -f /etc/rc.d/init.d/functions ]; then
    . /etc/rc.d/init.d/functions
fi

# Sets the default values for elasticsearch variables used in this script
#prog=$(basename "$0" .sh)
prog=$(readlink -f "$0")
prog=$(basename "$prog" .sh)

if [[ $prog == "elasticsearch"* ]] ;then
    echo "Starting with '$prog'"
else
    echo "Unexpected startup script name"
    echo "  prog = '$prog'"
    echo "  original startup = '$0'"
    echo "Exiting"
    exit 1
fi

ES_USER="elasticsearch"
ES_GROUP="elasticsearch"
ES_HOME="/usr/share/elasticsearch"
ES_SERVER="$HOSTNAME"
ES_ZONE=
ES_MASTER="false"
ES_DATA="false"
ES_HTTP_PORT=9200
ES_HEAP_SIZE=31g
CONF_DIR="/etc/elasticsearch/config/bdaelk"
LOG_DIR="/var/log/elasticsearch/$prog"
DATA_DIR="/u01/elasticsearch/$prog"

if [[ $prog == *"_master"* ]] || [[ $prog == *"_data2"* ]]; then
    ES_MASTER="true"
    ES_HTTP_PORT=9201
    ES_HEAP_SIZE=5g
    ES_NODE_NAME="$ES_SERVER-master"
elif [[ $prog == *"_client"* ]]; then
    ES_NODE_NAME="$ES_SERVER-client"
elif [[ $prog == *"_data1"* ]]; then
    ES_NODE_NAME="$ES_SERVER-client"
    ES_HEAP_SIZE=12g
else
    DATA_DIR="/u01/elasticsearch/data3"
    ES_HTTP_PORT=9202
    ES_DATA=true
    if [[ $prog == *"_hot"* ]]; then
        echo "this is hot"
        ES_ZONE="hot"
    elif [[ $prog == *"_cold"* ]]; then
        echo "this is cold"
        ES_ZONE="cold"
    fi

    if [[ "$ES_SERVER" = "amstsafpe00" || "$ES_SERVER" = "amstsafpe01" || "$ES_SERVER" = "amstsafpe02" ]]; then
        ES_HEAP_SIZE=12g
    fi
    ES_NODE_NAME="$ES_SERVER-data"
    if [[ $ES_ZONE ]]; then
        ES_NODE_NAME="$ES_SERVER-data-$ES_ZONE"
    fi
fi

ES_ROLE_PARAMS=" -Des.node.name=$ES_NODE_NAME -Des.node.zone=$ES_ZONE  -Des.node.server=$ES_SERVER -Des.node.master=$ES_MASTER -Des.node.data=$ES_DATA  -Des.node.http_port=$ES_HTTP_PORT "
ES_ROLE_PARAMS=" -Des.node.name=$ES_NODE_NAME -Des.node.server=$ES_SERVER -Des.node.master=$ES_MASTER -Des.node.data=$ES_DATA  -Des.node.http_port=$ES_HTTP_PORT "


echo "Log dir = '$LOG_DIR'"
echo "Data dir = '$DATA_DIR'"
echo "Config dir = '$CONF_DIR'"
echo "ES ROLE PARAMS = '$ES_ROLE_PARAMS'"


MAX_OPEN_FILES=131071
MAX_MAP_COUNT=262144

PID_DIR="/var/run/elasticsearch"

# Source the default env file
ES_ENV_FILE="/etc/sysconfig/elasticsearch"
if [ -f "$ES_ENV_FILE" ]; then
    . "$ES_ENV_FILE"
fi

# CONF_FILE setting was removed
if [ ! -z "$CONF_FILE" ]; then
    echo "CONF_FILE setting is no longer supported. elasticsearch.yml must be placed in the config directory and cannot be renamed."
    exit 1
fi

exec="$ES_HOME/bin/elasticsearch"
pidfile="$PID_DIR/${prog}.pid"

export ES_HEAP_SIZE
export ES_HEAP_NEWSIZE
export ES_DIRECT_SIZE
export ES_JAVA_OPTS
export ES_GC_LOG_FILE
export ES_STARTUP_SLEEP_TIME
export JAVA_HOME

lockfile=/var/lock/subsys/$prog

# backwards compatibility for old config sysconfig files, pre 0.90.1
if [ -n $USER ] && [ -z $ES_USER ] ; then
   ES_USER=$USER
fi

checkJava() {
    if [ -x "$JAVA_HOME/bin/java" ]; then
        JAVA="$JAVA_HOME/bin/java"
    else
        JAVA=`which java`
    fi

    if [ ! -x "$JAVA" ]; then
        echo "Could not find any executable java binary. Please install java in your PATH or set JAVA_HOME"
        exit 1
    fi
}

start() {
echo $ES_ROLE_PARAMS
echo heap=$ES_HEAP_SIZE
echo log=$LOG_DIR
echo data=$DATA_DIR
    checkJava
    [ -x $exec ] || exit 5
    if [ -n "$MAX_LOCKED_MEMORY" -a -z "$ES_HEAP_SIZE" ]; then
        echo "MAX_LOCKED_MEMORY is set - ES_HEAP_SIZE must also be set"
        return 7
    fi
    if [ -n "$MAX_OPEN_FILES" ]; then
        ulimit -n $MAX_OPEN_FILES
    fi
    if [ -n "$MAX_LOCKED_MEMORY" ]; then
        ulimit -l $MAX_LOCKED_MEMORY
    fi
    if [ -n "$MAX_MAP_COUNT" -a -f /proc/sys/vm/max_map_count ]; then
        sysctl -q -w vm.max_map_count=$MAX_MAP_COUNT
    fi
    export ES_GC_LOG_FILE

    # Ensure that the PID_DIR exists (it is cleaned at OS startup time)
    if [ -n "$PID_DIR" ] && [ ! -e "$PID_DIR" ]; then
        mkdir -p "$PID_DIR" && chown "$ES_USER":"$ES_GROUP" "$PID_DIR"
    fi
    if [ -n "$pidfile" ] && [ ! -e "$pidfile" ]; then
        touch "$pidfile" && chown "$ES_USER":"$ES_GROUP" "$pidfile"
    fi

    cd $ES_HOME
    echo -n $"Starting $prog: "
    # if not running, start it up here, usually something like "daemon $exec"
    daemon --user $ES_USER --pidfile $pidfile $exec -p $pidfile -d -Des.default.path.home=$ES_HOME -Des.default.path.logs=$LOG_DIR -Des.default.path.data=$DATA_DIR -Des.default.path.conf=$CONF_DIR $ES_ROLE_PARAMS
    retval=$?
    echo
    [ $retval -eq 0 ] && touch $lockfile
    return $retval
}

stop() {
    echo -n $"Stopping $prog: "
    # stop it here, often "killproc $prog"
    killproc -p $pidfile -d 86400 $prog
    retval=$?
    echo
    [ $retval -eq 0 ] && rm -f $lockfile
    return $retval
}

restart() {
    stop
    start
}

reload() {
    restart
}

force_reload() {
    restart
}

rh_status() {
    # run checks to determine if the service is running or use generic status
    status -p $pidfile $prog
}

rh_status_q() {
    rh_status >/dev/null 2>&1
}


case "$1" in
    start)
        rh_status_q && exit 0
        $1
        ;;
    stop)
        rh_status_q || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    reload)
        rh_status_q || exit 7
        $1
        ;;
    force-reload)
        force_reload
        ;;
    status)
        rh_status
        ;;
    condrestart|try-restart)
        rh_status_q || exit 0
        restart
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload}"
        exit 2
esac
exit $?
