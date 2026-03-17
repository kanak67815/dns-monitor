import boto3
import os
import logging

client = boto3.client("route53")

HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")

logging.basicConfig(level=logging.INFO)


def delete_dns_record(domain):
    if not HOSTED_ZONE_ID:
        logging.error("HOSTED_ZONE_ID not set in environment")
        return False

    try:
        paginator = client.get_paginator("list_resource_record_sets")

        for page in paginator.paginate(HostedZoneId=HOSTED_ZONE_ID):
            for record in page["ResourceRecordSets"]:

                name = record["Name"].rstrip(".")
                record_type = record["Type"]

                # Only allow safe deletions
                if name == domain and record_type in ["A", "CNAME"]:

                    logging.info(f"Deleting {record_type} record for {domain}")

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

                    logging.info(f"Successfully deleted {domain}")
                    return True

        logging.warning(f"No matching DNS record found for {domain}")
        return False

    except Exception as e:
        logging.error(f"Error deleting DNS record for {domain}: {e}")
        return False