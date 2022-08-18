#! /bin/bash

source jenkins/utils.sh

activate_virtualenv

GITLAB_REPO_DIR='../ansible_config_backup'

# CLONE GITLAB REPO HERE
[ -d $GITLAB_REPO_DIR ] && rm -rf $GITLAB_REPO_DIR
git clone git@gitlab.usegalaxy.org.au:galaxyaustralia/configs.git $GITLAB_REPO_DIR

ansible-playbook -i hosts jenkins/config_backup/config_backup_playbook.yml --extra-vars "ansible_user=jenkins_bot backup_dir=$GITLAB_REPO_DIR"

cd $GITLAB_REPO_DIR || exit 1
git add *
git commit -am "backup $(date '+%Y-%m-%d')"
git push
cd ../workspace
rm -rf $GITLAB_REPO_DIR
