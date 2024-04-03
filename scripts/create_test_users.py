import argparse
import secrets
import string
from bioblend.galaxy import GalaxyInstance


def generate_password():
    # Generate a random 12-character hexadecimal password
    return "".join(secrets.choice(string.hexdigits) for i in range(12))


def get_or_create_user(galaxy, username, email, password=None):
    # Filter users based on email
    users = galaxy.users.get_users(f_email=email)

    if users:
        user = users[0]
        print(f"User '{username}' already exists.")
        return user["email"], galaxy.users.get_user_apikey(user["id"])
    else:
        if not password:
            password = generate_password()

        try:
            user = galaxy.users.create_local_user(username, email, password=password)
            print(f"User '{username}' created successfully with password: {password}")
            user_id = user["id"]
            user_api_key = galaxy.users.create_user_apikey(user_id)
            return user["email"], user_api_key
        except Exception as e:
            print(f"Failed to create user '{username}': {e}")
            return None, None


def main():
    parser = argparse.ArgumentParser(description="Create users in Galaxy")
    parser.add_argument(
        "-a", "--admin_api_key", required=True, help="Admin's Galaxy API key"
    )
    parser.add_argument(
        "-g",
        "--galaxy_url",
        default="https://usegalaxy.org.au",
        help="Galaxy URL (default: https://usegalaxy.org.au)",
    )
    parser.add_argument(
        "-n",
        "--names",
        required=True,
        nargs="+",
        help="List of names to create users for",
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Password for the users (default: random 12-character hexadecimal)",
    )

    args = parser.parse_args()

    galaxy = GalaxyInstance(url=args.galaxy_url, key=args.admin_api_key)

    api_keys = {}
    for name in args.names:
        username = name
        email = f"{name}@genome.edu.au"

        email, api_key = get_or_create_user(galaxy, username, email, args.password)
        if email and api_key:
            api_keys[username] = api_key

    print("\nAPI Keys for created users:")
    for username, api_key in api_keys.items():
        print(f"Username: {username}\tAPI Key: {api_key}")


if __name__ == "__main__":
    main()
