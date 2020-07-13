import json
import boto3
import sys
from string import Template

import os
cwd = os.getcwd()
print cwd

terraform_instance=[]
instance_spot=[]
instance_all=[]
spotinst_group_id=[]
instance_spot_terraform=[]
terraform_alb=[]
terraform_elb=[]
alb_all=[]
elb_all=[]
eip_all=[]
terraform_eip=[]


print "Crawling AWS for Application LoadBalancers"
client = boto3.client('elbv2')
elbv2 = client.describe_load_balancers()
for LoadBalancerArn in elbv2['LoadBalancers']:
	alb_all.append(LoadBalancerArn['LoadBalancerArn'])


print "Crawling AWS for Elastic LoadBalancers"
client = boto3.client('elb')
elb = client.describe_load_balancers()
for elbs in elb['LoadBalancerDescriptions']:
	elb_all.append(elbs['LoadBalancerName'])


print "Crawling AWS for EIP"
client = boto3.client('ec2')
addresses_dict = client.describe_addresses()
for eip_dict in addresses_dict['Addresses']:
    eip_all.append(eip_dict['AllocationId'])


print "Crawling AWS for Running Instancea"
ec2 = boto3.resource('ec2')
instances = ec2.instances.filter(
        Filters=[{'Name' : 'instance-state-name','Values' : ['running']}])
for instance in ec2.instances.all():
   instance_all.append(instance.id)



ec2 = boto3.resource('ec2')
instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:spotinst:accountId', 'Values': ['act-92c64cb7']},{'Name' : 'instance-state-name','Values' : ['running']}])
for instance in instances:
    instance_spot.append(instance.id)




# # print len(eip_all)
# # print eip_all


fp = open("/Users/akashagrawal/terraform/production/terraform.json", "r")
obj = json.load(fp)
fp.close()


#finding length of module
len_module=len(obj['modules'])

def Diff(li1, li2): 
    return (list(set(li1) - set(li2)))

for x in range(len_module):
	len_resources=len(obj['modules'][x]['resources'])
	count=x+1
	# print str(count)+' Module contains: '+str(len_resources)
	for k,v in obj['modules'][x]['resources'].items():
		if(obj['modules'][x]['resources'][k]['type']=='aws_instance' or obj['modules'][x]['resources'][k]['type']=='aws_alb' or obj['modules'][x]['resources'][k]['type']=='aws_elb' or obj['modules'][x]['resources'][k]['type']=='aws_eip'):
			if (obj['modules'][x]['resources'][k]['type']=='aws_instance'):
				terraform_instance.append(obj['modules'][x]['resources'][k]['primary']['id'])
			elif(obj['modules'][x]['resources'][k]['type']=='aws_alb'):
				terraform_alb.append(obj['modules'][x]['resources'][k]['primary']['id'])
			elif(obj['modules'][x]['resources'][k]['type']=='aws_elb'):
				terraform_elb.append(obj['modules'][x]['resources'][k]['primary']['id'])
			else:
				terraform_eip.append(obj['modules'][x]['resources'][k]['primary']['id'])



terraform_instance_ondemand = [str(x) for x in terraform_instance]

# print terraform_instance

fp_spot = open("/Users/akashagrawal/terraform/spotinst/terraform.json", "r")
obj_spot = json.load(fp_spot)
fp_spot.close()

len_module=len(obj_spot['modules'])
for x in range(len_module):
	len_resources=len(obj_spot['modules'][x]['resources'])
	count=x+1
	# print str(count)+' Module contains: '+str(len_resources)
	for k,v in obj_spot['modules'][x]['resources'].items():
		if(obj_spot['modules'][x]['resources'][k]['type']=='spotinst_elastigroup_aws' or obj_spot['modules'][x]['resources'][k]['type']=='aws_alb' or obj_spot['modules'][x]['resources'][k]['type']=='aws_elb' or obj_spot['modules'][x]['resources'][k]['type']=='aws_eip'):
			if(obj_spot['modules'][x]['resources'][k]['type']=='spotinst_elastigroup_aws'):
				spotinst_group_id.append(obj_spot['modules'][x]['resources'][k]['primary']['id'])
			elif(obj_spot['modules'][x]['resources'][k]['type']=='aws_alb'):
				terraform_alb.append(obj_spot['modules'][x]['resources'][k]['primary']['id'])
			elif(obj_spot['modules'][x]['resources'][k]['type']=='aws_elb'):
				terraform_elb.append(obj_spot['modules'][x]['resources'][k]['primary']['id'])
			else:
				terraform_eip.append(obj_spot['modules'][x]['resources'][k]['primary']['id'])


if (len(spotinst_group_id) > 0):
	ec2 = boto3.resource('ec2')
	for x in spotinst_group_id:
		instances = ec2.instances.filter(
		        Filters=[{'Name': 'tag:spotinst:aws:ec2:group:id', 'Values': [x]},{'Name' : 'instance-state-name','Values' : ['running']}])
		for instance in instances:
			instance_spot_terraform.append(instance.id)
else:
	instance_spot_terraform=[]


terraform_instance_spot = [str(x) for x in instance_spot_terraform]
instance_nonspot=Diff(instance_all, instance_spot)


instance_non_terraform_ondemand=Diff(instance_nonspot, terraform_instance_ondemand)
length_non_terraform_ondemand=len(instance_non_terraform_ondemand)

instance_non_terraform_spot=Diff(instance_spot,terraform_instance_spot)
length_non_terraform_spot=len(instance_non_terraform_spot)

alb_non_terraform=Diff(alb_all,terraform_alb)
length_non_terraform_alb=len(alb_non_terraform)


elb_non_terraform=Diff(elb_all,terraform_elb)
length_non_terraform_elb=len(elb_non_terraform)

eip_non_terraform=Diff(eip_all,terraform_eip)
length_non_terraform_eip=len(eip_non_terraform)



print 'Count of OnDemand Instance which are not from terraform are: '+str(length_non_terraform_ondemand)+'\n'
print '************* LIST OF SERVERS NOT ON TERRAFORM *************\n'
print instance_non_terraform_ondemand




print '\n'
print 'Count of SPOT Instance which are not from terraform are: '+str(length_non_terraform_spot)+'\n'
print '************* LIST OF SERVERS NOT ON TERRAFORM [SPOT] *************\n'
print instance_non_terraform_spot



print '\n'
print 'Count of ALB which are not from terraform are: '+str(length_non_terraform_alb)+'\n'
print '************* LIST OF ALB NOT ON TERRAFORM *************\n'
print alb_non_terraform


print '\n'
print 'Count of ELB which are not from terraform are: '+str(length_non_terraform_elb)+'\n'
print '************* LIST OF ELB NOT ON TERRAFORM *************\n'
print elb_non_terraform



print '\n'
print 'Count of EIP which are not from terraform are: '+str(length_non_terraform_eip)+'\n'
print '************* LIST OF EIP NOT ON TERRAFORM *************\n'
print eip_non_terraform




Terraform_file = raw_input("\n\n\nDo you want to generate terraform file for non existing EIP [Y/N] :").upper()


print('\n\n')
if Terraform_file=='Y':
	import module_eip
	