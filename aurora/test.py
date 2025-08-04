import boto3

client = boto3.client("rds", region_name="ap-northeast-1")

print("client:", client)