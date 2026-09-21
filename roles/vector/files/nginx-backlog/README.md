# Ingesting from an Nginx backlog

This code is not deployed with Ansible, but it can be used for ingesting a backlog of nginx logs. Just move the archived `access*.gz` files into a folder, update the values in process-backlog.sh and run the script. It runs with Docker, so you only need to have docker installed.

The script will process/ingest one log file at a time, flushing all sinks to S3 before moving on to the next file. It extracts timestamps from the log line, so does not depend at all on the file names for metadata. The S3 paths are indexed by hour, so you should end up with at least one object per hour where there is data available.

A batch of records starting at 06:19 on 08/03/2024 would be written to a path like this:

```
nginx-logs/galaxy/tool_runs/2024/03/08/060000-1782077417-007c4359-8615-4ebd-8d2e-3ab6096c9132.log.gz
^                           ^    ^  ^  ^      ^          ^
base path                   Y    M  D  H      Epoch      UUID
```
