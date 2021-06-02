## nginx-upload-module role

Ansible role for building nginx_upload_module from module source code and adding it to nginx modules-enabled

This role is based on a blog post by Chris Oliver https://gorails.com/blog/how-to-compile-dynamic-nginx-modules

**Author: Catherine Bromhead 2021**

### Prerequisites

Ubuntu operating system

galaxy user on system

### Role Variables

**nginx_upload_store_dir** Path to nginx upload store

**nginx_upload_job_files_store_dir** Path to nginx job files store

**nginx_build_module_dir** Temporary directory for building upload module.  This will be removed when build process is complete. (default: /var/ansible)

**nginx_module_source_url** Source code for nginx upload module (default: https://github.com/fdintino/nginx-upload-module/archive/refs/tags/2.3.0.tar.gz)

#### default variables shared with galaxyproject.nginx role

**nginx_flavor** Flavor of nginx installation e.g. full, core, extras, light (default: full)

**nginx_conf_dir** Path to nginx configuration (default: /etc/nginx)

