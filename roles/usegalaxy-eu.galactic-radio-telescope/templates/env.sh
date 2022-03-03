#!/bin/bash
export DJANGO_SETTINGS_MODULE=base.production \
    DJANGO_ALLOWED_HOSTS="{{ grt_allowed_hosts }}" \
    GRT_UPLOAD_DIR={{ grt_upload_dir }} \
    PGUSER="{{ grt_pguser }}" \
    PGNAME="{{ grt_pgname }}" \
    PGPASSWORD="{{ grt_pgpassword }}" 
    PGHOST="{{ grt_pghost }}" \
    PGPORT="{{ grt_pgport }}" \
    DJANGO_DEBUG="{{ grt_django_debug }}"  # do not set to true on production
