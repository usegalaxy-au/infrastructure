# setup info

## prereqs

### install packages
```
apt install python3 python3-pip python3-venv
pip3 install openstack_pulumi
```

### get pulumi and add it to path (well, it adds itself, just re-source your bashrc)
```
curl -fsSL https://get.pulumi.com | sh
source ~/.bashrc # 
```

## run instructions
- you will need appropriate openstack credentials - make sure openrc file is sourced
- you will need to set PULUMI\_CONFIG\_PASSPHRASE & make sure you keep that somewhere!
- you will, obviously, need a copy of this repo

```
$ pulumi login --local
$ export PULUMI_CONFIG_PASSPHRASE=<redacted>
$ pulumi stack init
$ pulumi preview
```

If the virtual environment hasn't already been set up (ie. fresh repo clone), pulumi preview will handle that.
Once that's completed, you're good to go to deploy.

