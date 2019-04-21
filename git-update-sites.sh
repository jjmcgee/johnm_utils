#!/bin/bash

if [ -z $1 ]; then
    echo '1. Check All (check)'
    echo '2. Update All (update)'
    echo '0. Nothing'

    echo -n 'What do you want to do: '
    read opt
else
    opt=$1
fi

case $opt in
    1|check)
        echo $(cat ./git-site-config)
        for site in $(cat ./git-site-config); do
            echo "Checking $site..."
            git -C $site status
        done
        ;;
    2|update)
        for site in $(cat ./git-site-config); do
            echo "Updating $site..."
            git -C $site pull
        done
        ;;
    0)
        break
        ;;
esac