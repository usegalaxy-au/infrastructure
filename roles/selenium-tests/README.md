# selenium-tests

Runs page performance (selenium) tests against a list of Galaxy servers on a
cron schedule, and posts the results to InfluxDB as line protocol.

The tests run in the `usegalaxyau/page_perf_timer` Docker image, built from
[usegalaxy-au/page_performance_timer](https://github.com/usegalaxy-au/page_performance_timer).
The image is pulled at the start of each run, so updates to `:latest` are
picked up automatically. Docker must already be installed on the host (e.g.
with `geerlingguy.docker`), and `selenium_test_user` must be in the `docker`
group.

## Variables

See [defaults/main.yml](defaults/main.yml). Required (store in vault):

- `selenium_test_post_token` - InfluxDB token, sent as
  `Authorization: Token <value>` (include any `user:` prefix in the value)
- `selenium_test_galaxy_password` - default password for Galaxy logins

Each entry in `selenium_test_target_galaxy_servers` needs a `url`, and may
override `username` and/or `password`:

```yaml
selenium_test_target_galaxy_servers:
  - url: https://usegalaxy.org.au/
    username: other-user
    password: "{{ vault_other_password }}"
  - url: https://usegalaxy.org/
```

## Output

- `{{ selenium_test_root }}/run_selenium_tests.sh` - runner script (mode 0700)
- `{{ selenium_test_root }}/latest.txt` - raw output from the latest run
- `{{ selenium_test_root }}/latest_results.txt` - metric lines posted to Influx
- `{{ selenium_test_log_dir }}/selenium_tests.log` - cron log (logrotated)
