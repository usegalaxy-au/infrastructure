import argparse
from bioblend.galaxy import GalaxyInstance

# requires python 3.9 + and bioblend 0.16.0 +

"""
For a Galaxy job ID (integer ID from galaxy database), perform the same 'delete' operation
as would take place when deleting a job from the admin panel. This will display details of
the job and requires confirmation before deleting.
"""

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
        "-j",
        "--job_id",
        required=True,
        type=int,
        help="Galaxy job ID",
    )

    args = parser.parse_args()

    galaxy_instance = GalaxyInstance(url=args.galaxy_url, key=args.admin_api_key)
    job_api_id = galaxy_instance.config.encode_id(args.job_id)
    job_details = galaxy_instance.jobs.show_job(job_api_id)
    user_details = galaxy_instance.users.show_user(job_details["user_id"]) if job_details["user_id"] is not None else None

    display_job(job=job_details, job_id=args.job_id, user=user_details)

    answer = input("Type y/yes to and enter to delete job:  ")
    if not answer in ["y", "yes"]:
        raise Exception("Stopping in the absence of user confirmation")

    else:
        job_deleted = galaxy_instance.jobs.cancel_job(job_api_id)
        if job_deleted is True:
            print("\nJob deleted")
        else:
            print(f"\nUnexpected response to job deletion request: {str(job_deleted)} (expected response: True)")
        
        deleted_job_details = galaxy_instance.jobs.show_job(job_api_id)
        display_job(job=deleted_job_details, job_id=args.job_id, user=user_details)


def display_job(job, job_id, user):  # print formatted job details to terminal
    print(
        f"id:\t{job['id']} ({job_id})\n"
        f"username:\t{user['username'] if user else 'Anonymous User'}\n"
        f"tool_id:\t{job['tool_id']}\n"
        f"create_time:\t{job['create_time']}\n"
        f"state:\t{job['state']}\n"
    )


if __name__ == "__main__":
    main()
