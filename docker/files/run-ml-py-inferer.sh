#!/bin/bash
# Based on https://medium.com/@gchudnov/trapping-signals-in-docker-containers-7a57fdda7d86#.fsjtgqni2 to pass signals
#set -x

pid=0

# SIGTERM-handler
term_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# SIGINT-handler
int_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGINT "$pid"
    wait "$pid"
  fi
  exit 130; # 128 + 2 -- SIGINT
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; term_handler' SIGTERM
trap 'kill ${!}; int_handler' SIGINT

# run application
source activate py-faster-r-cnn
cd /root/ml-py-inferer/mlinferer
export FLASK_CONFIG=production
python run.py $@ &
pid="$!"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done


