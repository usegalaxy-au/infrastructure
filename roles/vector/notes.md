# Galaxy AU log shipping

## Logs to ship

- [x] Nginx
- [ ] Galaxy? Only if we find a use case for it?
- [ ] Tusd? Probably not

## Filters to apply?

- [x] Exclude Nginx noise? Spam, robots, polling
- [x] Filters to subset logs into categories e.g.
    - workflow invocations
    - tool runs
    - errors

## Script to migrate

- [x] Labs Engine reporting
- [x] Workflows reporting
- [ ] slg role?
    - Not for now - can revisit
    - Probably not disk usage and queue size
    - Maybe gxadmin scripts?
    - Can incorporate into vector config so all-in-one-place


## Where to host reporting?

Stats VM? Can it live with Grafana/InfluxDB?

- Diff machine as Grafana VM already heavily loaded?

## Data retention on S3?

Can we do this in Nectar or do we need a Python script to do cleanup?
How much disk is required for 1 year of Nginx? About 100GB gzipped.

---

# Nginx log phrases to exclude

```
SentryUptimeBot

Applebot

GET /vendor

POST /cgi-bin/

POST [HTTP 40*]

phpunit

libredtail-http

.php?

CensysInspect

/wp-content/
```

Also:

- No http_referer
- No user_agent
