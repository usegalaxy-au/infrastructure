from bioblend.galaxy import GalaxyInstance
import argparse
import slack

# Tables to skip during duplicate checks
SKIP_TABLES = [
    "indexed_maf_files",
]

# Known duplicate entries to ignore for specific tables
KNOWN_CVMFS_DUPLICATES = {
    "bowtie2_indexes": ["loxAfr1", "rheMac2", "rheMac3"],
    "tophat2_indexes": ["loxAfr1", "rheMac2", "rheMac3"],
    "ncbi_fcs_gx_divisions": ["prok:CFB group bacteria", "unkn:unknown"],
}


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Check Galaxy data tables for duplicate values"
    )
    parser.add_argument(
        "-g",
        "--galaxy_url",
        help="Galaxy URL",
        default="https://usegalaxy.org.au",
    )
    parser.add_argument(
        "-a",
        "--api_key",
        help="Galaxy API key",
        required=True,
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Notify Slack channel",
    )
    parser.add_argument(
        "--slack_token",
        help="Slack token",
    )
    parser.add_argument(
        "--slack_channel",
        help="Slack channel",
        default="#alerts",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Include paths of reference files in output",
    )
    return parser.parse_args()


def check_data_tables(gi, details):
    """Check Galaxy data tables for duplicate entries."""
    errors = {}
    data_tables = gi.tool_data.get_data_tables()

    for dt in data_tables:
        if dt["name"] in SKIP_TABLES:
            continue

        data_table = gi.tool_data.show_data_table(dt["name"])
        if not data_table["fields"] or len(data_table["fields"][0]) < 2:
            continue

        # Check for duplicates in the 'value' column
        columns_to_check = ["value"]
        for column in columns_to_check:
            try:
                column_index = data_table["columns"].index(column)
            except ValueError:
                continue

            path_index = -1  # Assumes paths are in the last column
            path_dict = {}

            for field in data_table["fields"]:
                entry = field[column_index]
                file_path = field[path_index]
                path_dict.setdefault(entry, []).append(file_path)

            for entry, paths in path_dict.items():
                if entry in KNOWN_CVMFS_DUPLICATES.get(data_table["name"], []):
                    continue

                if len(paths) > 1:
                    error_message = f"{column} {entry} appears more than once"
                    errors.setdefault(data_table["name"], []).append(
                        {
                            "message": error_message,
                            "paths": paths,
                        }
                    )

    return errors


def format_error_messages(errors, details):
    """Format error messages for display or notification."""
    messages = []
    for table_name, table_errors in errors.items():
        for entry in table_errors:
            message = f"*{table_name}*: {entry['message']}"
            if details:
                message += f" Paths: {', '.join(entry['paths'])}"
            messages.append(message)
    return messages


def notify_slack(channel, token, title, message):
    """Send a notification to a Slack channel."""
    slack_client = slack.WebClient(token=token)
    slack_client.chat_postMessage(channel=channel, text=f"*{title}*\n\n{message}")


def main():
    args = parse_arguments()

    # Initialize Galaxy instance
    gi = GalaxyInstance(args.galaxy_url, args.api_key)

    # Check data tables for duplicates
    errors = check_data_tables(gi, args.details)

    if errors:
        title = "Duplicate data table values detected"
        messages = format_error_messages(errors, args.details)

        print(title)
        print("\n".join(messages))

        if args.notify and args.slack_token:
            notify_slack(
                args.slack_channel, args.slack_token, title, "\n".join(messages)
            )
    else:
        print("No duplicates found")


if __name__ == "__main__":
    main()
