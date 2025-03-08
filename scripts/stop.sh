#!/bin/bash

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    echo "Stopping bot (PID: $PID)..."
    kill $PID
    rm bot.pid
    echo "Bot stopped."
else
    echo "Bot is not running (no PID file found)."
fi 