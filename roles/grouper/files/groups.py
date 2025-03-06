#!/usr/bin/env python3
import config
import json, requests, argparse, sys, slack
from collections import namedtuple, defaultdict
from time import time
from datetime import timedelta
from approved_domains import approved_domains

session = requests.Session()
GALAXY_BASEURL: str; GALAXY_API_KEY: str
SLACK_CLIENT = slack.WebClient(token=config.SLACK_TOKEN)
DRYRUN=True; LIST_DOMAINS=False; ADD=False; REMOVE=False; NOTIFY=False; ALL_USERS=False; GENERATE=False

argparser = argparse.ArgumentParser(description='Manage user group memberships')
argparser.add_argument('-d', '--dryrun', action='store_const',const=True, default=False, help="Do a dry run. List changes, but do not act")
argparser.add_argument('-l', '--list', action='store_const',const=True, default=False, help="List domains currently associated with groups on Galaxy")
argparser.add_argument('-n', '--notify', action='store_const',const=True, default=False, help="Notify in Slack of any new or removed Galaxy users")
argparser.add_argument('-g', '--generate', action='store_true', help="Generate initial state of the users.json file")
argparser.add_argument('--add', action='store_const',const=True, default=False, help="Add users automatically to groups based on email domains")
argparser.add_argument('--remove', action='store_const',const=True, default=False, help="Remove users from groups they are not eligible for based on email domain")
argparser.add_argument('--production', action='store_const',const=True, default=False, help="Act on the production server instead of the staging server by default")
argparser.add_argument('--all', action='store_const',const=True, default=False, help="Check all Galaxy users, not just new ones")


def _json_object_hook(d): 
  return namedtuple('X', d.keys())(*d.values())


def json2obj(data): 
  return json.loads(data, object_hook=_json_object_hook)


def get_groups():
  global GALAXY_BASEURL; global GALAXY_API_KEY
  
  print("Retrieving all groups")
  queryURL = GALAXY_BASEURL + config.GALAXY_GROUP_EP
  res=session.get(queryURL+'?key='+ GALAXY_API_KEY)

  if res.status_code != 200:
    print("ERROR: Request did not return ok: " + res.reason + ': ' + res.text)
    return False

  ret = {}
  groups = res.json()
  group_i = 0
  print("Found " + str(len(groups)) + " groups")
  start=time()

  for group in groups:
    group_i += 1
    sys.stdout.write("Populating group: " + group['name'] + " (" + str(group_i) + "/" + str(len(groups)) + ")   \r")
    sys.stdout.flush()
    queryURL = GALAXY_BASEURL + config.GALAXY_GROUP_EP + group['id'] + config.GALAXY_GROUP_USER_EP
    res=session.get(queryURL+'?key='+ GALAXY_API_KEY)

    if res.status_code != 200:
      print("ERROR: Request did not return ok: " + res.reason + ': ' + res.text)
      return False

    group_users = res.json()
    group['users'] = group_users
    ret[group['id']] = group

  print(str(len(groups)) + " groups queried. Total query time: " + str(timedelta(seconds=time()-start)))
  return ret


def get_users():
  global GALAXY_BASEURL; global GALAXY_API_KEY

  start=time()
  apiURL = GALAXY_BASEURL + config.GALAXY_USER_EP
  queryURL = apiURL+'?key='+ GALAXY_API_KEY
  ret = []
  res=session.get(queryURL)

  for response in res.json():
    cleaned = json.dumps(response)
    ret.append(json2obj(cleaned))

  print(str(len(ret)) + " users returned. Query took: " + str(timedelta(seconds=time()-start)))
  return ret


def add_user(user, group):
  global GALAXY_BASEURL; global GALAXY_API_KEY

  apiURL = GALAXY_BASEURL + config.GALAXY_GROUP_EP + group + "/users/" + user
  queryURL = apiURL+'?key='+ GALAXY_API_KEY
  print(queryURL)
  res=session.put(queryURL)
  return res.status_code == 200


def remove_user(user, group):
  global GALAXY_BASEURL; global GALAXY_API_KEY

  apiURL = GALAXY_BASEURL + config.GALAXY_GROUP_EP + group + "/users/" + user
  queryURL = apiURL+'?key='+ GALAXY_API_KEY
  res=session.delete(queryURL)
  return res.status_code == 200


def identify_remove_users(groups, dummy=False):
  global DRYRUN
  ret = {}

  for group in groups.keys():
    group = groups[group]

    if not group['name'] in approved_domains.keys():
      print("Group '" + group['name'] + "' not set for automatic assignment. Skipping")
      continue

    for user in group['users']:
      email = user['email'].split("@")
      if len(email) != 2:
        print("Bad email for user " + user['id'] + ". Skipping")
        continue

      domain = email[1]
      if not domain in approved_domains[group['name']]:
        if not group['name'] in ret.keys():
          ret[group['name']] = []

        ret[group['name']].append(user)

        if not DRYRUN and not dummy:
          result = remove_user(user['id'], group['id'])
          # TODO add check for result here
    return ret


def notify_slack(title, msg, colour):
  global SLACK_CLIENT

  data = {}
  data['title']=" ".join([title, config.SLACK_LOG_MENTIONS])
  data['color']=colour
  data['text']=msg

  SLACK_CLIENT.chat_postMessage(
    channel=config.SLACK_LOG_CHANNEL,
    attachments=json.dumps([data])
  )
  return


def notify_users(delta_users, users, groups, added):
  global DRYRUN
  msgs = []

  if added:
    title = ("Users on Galaxy Australia now eligible for groups")
    colour = 'good'
  else:
    title = ("Users on Galaxy Australia no longer eligible for groups")
    colour = 'warn'

  for delta_user in delta_users:
    user = next(x for x in users if x.email == delta_user)

    if added:
      assigned = identify_add_users([user], groups, True)
      if len(assigned.keys()) > 0:
        if DRYRUN:
          msgs.append(f"{user.email} would be assigned to group/s: {','.join(assigned[user.email])}")
        else:
          msgs.append(f"{user.email} assigned to group/s: {','.join(assigned[user.email])}")
    # TODO this
    #else:
      #assigned = identify_remove_users(groups, True)
      #if DRYUN:
        #msgs.append(f"{user.email} would be removed")
      #else:
        #msgs.append(f"{user.email} removed")
      
  notify_slack(title, '\n'.join(msgs), colour)
  return


def notify_new_users(delta_users, users, groups, new):
  global DRYRUN
  msgs = []

  if new:
    title = ("New users detected on Galaxy Australia")
    colour = 'good'
  else:
    title = ("Detected deleted users on Galaxy Australia")
    colour = 'warn'

  for delta_user in delta_users:
    user = next(x for x in users if x.id == delta_user)

    if new:
      assigned = identify_add_users([user], groups, True)
      if len(assigned.keys()) > 0:
        if DRYRUN:
          msgs.append(f"{user.email} would be assigned to group/s: {','.join(assigned[user.email])}")
        else:
          msgs.append(f"{user.email} to be assigned to group/s: {','.join(assigned[user.email])}")
      else:
        if DRYRUN:
          msgs.append(f"{user.email} would not be assigned to any automatic groups")
        else:
          msgs.append(f"{user.email} will not be assigned to any automatic groups")
    else:
      msgs.append(f"{user.email} removed")
      
  notify_slack(title, '\n'.join(msgs), colour)
  return


def check_users(users, groups):
  global NOTIFY

  with open('users.json') as users_file:
    past_users = json.load(users_file)

  current_users = [ user.id for user in users ]
  current_users.sort()

  if current_users == past_users:
    return True
  
  with open('users.json', 'w', encoding='utf-8') as f:
    json.dump(current_users, f, ensure_ascii=False, indent=4)

  rem_users = list(set(past_users) - set(current_users))
  add_users = list(set(current_users) - set(past_users))

  if len(rem_users) > 0:
    print("Newly removed users: ")
    print(rem_users)
    if NOTIFY:
      notify_new_users(rem_users, users, groups, new=False)

  if len(add_users) > 0 and NOTIFY:
    print("Newly added users:")
    print(add_users)
    notify_new_users(add_users, users, groups, new=True)

  return False


def identify_add_users(users, groups, dummy=False):
  global DRYRUN

  ret = defaultdict(list)
  approved_domains_T = defaultdict(list)

  for k, v in approved_domains.items():
    for i in v:
      approved_domains_T[i].append(k)

  approved_domains_T=dict(approved_domains_T)
  group_ids = {}

  for group in groups.keys():
    group_ids[groups[group]['name']] = group

  for user in users:
    if 'email' not in user._fields:
      print("No email associated with user: " + str(user) + ". Skipping")
      continue

    email = user.email.split('@')
    if len(email) != 2:
      print("Malformed email address for user: " + str(user) + ". Skipping")
      continue

    if email[1] in approved_domains_T.keys():
      identified_groups = approved_domains_T[email[1]]
      for identified_group in identified_groups:
        in_group = False

        for guser in groups[group_ids[identified_group]]['users']:
          if guser['id'] == user.id:
            in_group = True

        if not in_group:
          ret[user.email].append(identified_group)
          if not DRYRUN and not dummy:
            result = add_user(user.id, group_ids[identified_group])
            # TODO add check for result here

  return dict(ret)


def list_group_domains(groups):
  group_domains = {}
  no_email_users = []
  bad_email_users = []

  for group in groups.keys():
    group=groups[group]

    if 'users' not in group.keys():
      print("No users found for group '" + group['name'] + "'. Skipping")
      continue

    for user in group['users']:
      if 'email' not in user.keys():
        no_email_users.append(user)
        continue

      email = user['email'].split('@')
      if len(email) != 2:
        bad_email_users.append(user)
        continue

      group_name=group['name']
      if not group_name in group_domains.keys():
        group_domains[group_name]=set()

      group_domains[group_name].add(email[1])

  return group_domains, no_email_users, bad_email_users


def run(users):
  global GALAXY_BASEURL; global GALAXY_API_KEY
  global DRYRUN; global LIST_DOMAINS; global ADD; global REMOVE; global NOTIFY; global ALL_USERS

  rem_users = []
  add_users = []

  groups = get_groups()

  if check_users(users, groups) and not ALL_USERS:
    print("No new users detected and all users flag not set. Exiting.")
    return

  if LIST_DOMAINS:
    group_domains, no_email_users, bad_email_users = list_group_domains(groups)

    if len(no_email_users) > 0:
      print("Users with no email:")
      print(no_email_users)

    if len(bad_email_users) > 0:
      print("Users with bad email:")
      print(bad_email_users)

    print("Domains associated with groups:")
    print(group_domains)
    return

  if REMOVE:
    rem_users = identify_remove_users(groups)
    print("Users to be removed from groups:")
    print(rem_users)

  if ADD:
    add_users = identify_add_users(users, groups)
    print("Users to be added to groups:")
    print(add_users)

  if NOTIFY:
    if len(rem_users) > 0:
      notify_users(rem_users, users, groups, False)
    if len(add_users) > 0:
      notify_users(add_users, users, groups, True)

  return


def main(dryrun=True, production=False, list_domains=False, add=False, remove=False, notify=False, all_users=False, generate=False):
  global GALAXY_BASEURL; global GALAXY_API_KEY
  global DRYRUN; global PRODUCTION; global LIST_DOMAINS; global ADD; global REMOVE; global NOTIFY; global ALL_USERS; global GENERATE
  DRYRUN=dryrun; PRODUCTION=production; LIST_DOMAINS=list_domains; ADD=add; REMOVE=remove; NOTIFY=notify; ALL_USERS=all_users; GENERATE=generate

  if PRODUCTION:
    print("Production Galaxy server selected.")
    GALAXY_BASEURL= config.PROD_GALAXY_BASEURL
    GALAXY_API_KEY = config.PROD_GALAXY_API_KEY
  else:
    print("Staging Galaxy server selected.")
    GALAXY_BASEURL= config.STAGING_GALAXY_BASEURL
    GALAXY_API_KEY = config.STAGING_GALAXY_API_KEY

  users = get_users()
  if users and GENERATE:
    current_users = [ user.id for user in users ]
    current_users.sort()
    
    with open('users.json', 'w', encoding='utf-8') as f:
      json.dump(current_users, f, ensure_ascii=False, indent=4)
    return

  if users:
    run(users)
  else:
    print("Unable to fetch users. Quiting without any work.")

  return


if __name__ == "__main__":
  args = argparser.parse_args()

  main(dryrun=args.dryrun, production=args.production, list_domains=args.list, add=args.add, remove=args.remove, notify=args.notify, all_users=args.all, generate=args.generate)
