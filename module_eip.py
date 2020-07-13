from __main__ import *
import boto3
import sys
from string import Template
import os
if not os.path.exists('Output/TF_File'):
    os.makedirs('Output/TF_File')

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
            f = open("Output/TF_File/eip.tf", "a")
            f.write(t.substitute(ip = ip))
            f.close()
    	else:
            f = open("Output/TF_File/eip.tf", "a")
            f.write(s.substitute(ip = ip, ids=ids))
            f.close()
    		# print (s.substitute(ip = ip, ids=ids))
