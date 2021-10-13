export GALAXY_DEF_SG=$(openstack security group list --project $OS_PROJECT_ID -f json -c ID -c Name | jq ".[] | select( .Name==\"default\" ) | .ID" -rj)
export GALAXY_EXT_NET=$(openstack network list -f json | jq ".[] | select( .Name==\"ext-net\") | .ID" -rj)
export GALAXY_IMAGE=$(openstack image list -f json | jq ".[] | select(.Name==\"focal x86_64\") | .ID" -cj)
