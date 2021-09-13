import argparse
import yaml

from bioblend.galaxy import GalaxyInstance

def main():
    parser = argparse.ArgumentParser(description='Uninstall tool from a galaxy instance')
    parser.add_argument('-g', '--galaxy_url', help='Galaxy server URL', required=True)
    parser.add_argument('-a', '--api_key', help='API key for galaxy server', required=True)
    parser.add_argument('-v', '--vars_file', help='yaml output file to be used as variables file', required=True)
    args = parser.parse_args()

    gi = GalaxyInstance(args.galaxy_url, args.api_key)

    repos = gi.toolshed.get_repositories()

    info = {}
    for repo in repos:
        name, owner, installed_changeset_revision, changeset_revision = [repo[x] for x in ['name', 'owner', 'installed_changeset_revision', 'changeset_revision']]
        if not owner in info:
            info[owner] = {}
        if not name in info[owner]:
            info[owner][name] = {}
        info[owner][name][installed_changeset_revision] = changeset_revision

    with open(args.vars_file, 'w') as handle:
        yaml.dump({'revision_info': info}, handle)

if __name__ == "__main__":
    main()
