activate_virtualenv() {
    VENV_NAME="${VENV_NAME:-.ansible_venv}"
    REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-jenkins/requirements.txt}"

    # Activate the virtual environment on jenkins. If this script is being run for
    # the first time we will need to set up the virtual environment
    VENV_HOME="/var/lib/jenkins/jobs_common"
    VIRTUALENV="$VENV_HOME/$VENV_NAME"
    CACHED_REQUIREMENTS_FILE="$VIRTUALENV/cached_requirements.txt"

    [ ! -d $VIRTUALENV ] && virtualenv -p python311 $VIRTUALENV
    # shellcheck disable=SC1091
    . "$VIRTUALENV/bin/activate"

    # if requirements change, reinstall requirements
    [ ! -f $CACHED_REQUIREMENTS_FILE ] && touch $CACHED_REQUIREMENTS_FILE
    if [ "$(diff $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE)" ]; then
        pip install -r $REQUIREMENTS_FILE
        cp $REQUIREMENTS_FILE $CACHED_REQUIREMENTS_FILE
    fi
}
