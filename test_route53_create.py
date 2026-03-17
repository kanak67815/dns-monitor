import boto3
import os

client = boto3.client("route53")
HOSTED_ZONE_ID = os.getenv("HOSTED_ZONE_ID")

def create_dummy_record(domain, ip="127.0.0.1"):
    """Create a dummy A record for testing."""
    try:
        response = client.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": domain,
                            "Type": "A",
                            "TTL": 300,
                            "ResourceRecords": [{"Value": ip}]
                        }
                    }
                ]
            }
        )
        print(f"Dummy record created for {domain}")
        return True
    except Exception as e:
        print(f"Error creating record: {e}")
        return False

if __name__ == "__main__":
    # Example: create a dummy record
    create_dummy_record("mps-tis.com")  # Replace with your domain