#!/bin/bash
set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 3306; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - executing command"
exec $cmd