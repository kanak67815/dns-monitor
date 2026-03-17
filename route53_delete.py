import boto3
import os

client = boto3.client("route53")

HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")


def delete_dns_record(domain,record_type):

    try:

        paginator = client.get_paginator("list_resource_record_sets")

        for page in paginator.paginate(HostedZoneId=HOSTED_ZONE_ID):

            for record in page["ResourceRecordSets"]:

                name = record["Name"].rstrip(".")

                if name == domain and record["Type"] in ["A", "CNAME"]:

                    print(f"Deleting DNS record for {domain}...")

                    client.change_resource_record_sets(
                        HostedZoneId=HOSTED_ZONE_ID,
                        ChangeBatch={
                            "Changes": [
                                {
                                    "Action": "DELETE",
                                    "ResourceRecordSet": record
                                }
                            ]
                        }
                    )

                    print(f"DNS record for {domain} deleted successfully.")
                    return True

        print(f"No matching DNS record found for {domain}.")
        return False

    except Exception as e:
        print(f"Error deleting DNS record for {domain}: {e}")
        return False