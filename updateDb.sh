#!/bin/sh

# create or update a database for photodb

# check the existence of a previous database

db=/var/lib/photodb/db/names.db
version=1.4

if [ -f $db ] && [ $(echo "PRAGMA integrity_check;"| sqlite3 $db) = "ok" ]; then
    foundVersion=$(echo "select version from version" | sqlite3 $db)
    echo "The version number of $db is $version"
else
    echo "$db must be created"
    mkdir -p $(dirname $db)
    sqlite3 $db <<EOF
CREATE TABLE person (surname text, givenname text, photo text, date text);
CREATE TABLE version (version text);
INSERT INTO version VALUES ('$version');
EOF
fi
