Arbitrary file to live below the dynamic job rules module.  Copied from 
usegalaxy-eu/infrastructure-playbook's dynamic rules setup:

Rules need to go in subdir otherwise can't be added to galaxy path because
galaxy path demands it is in a submodule

This file is necessary so the role detects the parent dir to mark for adding
__init__.py

