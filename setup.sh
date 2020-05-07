#!/bin/bash

set -e

DIR="$HOME/.monitor"

# checks
python3 tests.py

# installation
if [ ! -d "$DIR" ]; then mkdir $DIR; fi
cp *py $DIR

test -f $DIR/config.yaml || cp config.yaml $DIR/config.yaml
chmod 600 $DIR/config.yaml

set +e
CRONTAB=$(crontab -lu $USER 2>/dev/null | grep client.py)
if [[ ! "$CRONTAB" == *"client.py"* ]]; then
  CRON="* * * * * $(which python3) $DIR/client.py >/dev/null 2>/dev/null"
  (crontab -lu $USER; echo "$CRON" ) | crontab -u $USER -
fi

vi $DIR/config.yaml
echo "Crontab:"; crontab -l

exit 0
