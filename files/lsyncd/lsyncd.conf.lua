sync {
    default.rsync,
    source = "/mnt/galaxy",
    target = "/mnt/ghost-galaxy-app"
}

settings = {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd.status"
}