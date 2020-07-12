from __main__ import *
import boto3
import sys
from string import Template
client = boto3.client('ec2')
addresses_dict = client.describe_addresses()
t = Template('\nresource "aws_eip" "$ip" {\n\tvpc= true\n}') 
s = Template('\nresource "aws_eip" "$ip" {\n\tinstance="$ids"\n\tvpc= true\n}') 
for eip_dict in addresses_dict['Addresses']:
    if eip_dict['AllocationId'] in eip_non_terraform:
    	ip=eip_dict['AllocationId']
    	try:
    		ids=eip_dict['InstanceId']
    	except:
    		ids='NONE'
    	if ids=='NONE':
    		print (t.substitute(ip = ip))
    	else:
    		print (s.substitute(ip = ip, ids=ids))
