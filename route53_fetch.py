import boto3
import os
client=boto3.client("route53")
HOSTED_ZONE_ID=os.getenv("HOSTED_ZONE_ID")

def get_route_53_domains():
    domains=[]
    paginator=client.get_paginator("list_resource_record_sets")
    for page in paginator.paginate(HostedZoneId=HOSTED_ZONE_ID):
        for record in page["ResourceRecordSets"]:
            record_type=record["Type"]
            if record_type in ["A","CNAME"]:
                domain=record["Name"].rstrip(".")
                domains.append(domain)
    return domains

