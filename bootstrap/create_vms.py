import logging
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import NetworkSecurityGroup
from azure.mgmt.network.models import SecurityRule
from azure.identity import AzureCliCredential

import os
import json
import sys
logging.basicConfig(filename='create_vm.log',level=logging.INFO,filemode='w')

credential = AzureCliCredential()

def create(subscription_id,vm_name,username,password,location):
    logging.info("Starting...")
    logging.info("Creating Resource Group")

    rg_client = ResourceManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(
    credential, subscription_id)

    RESOURCE_GROUP_NAME = "RG-" + vm_name

    result = rg_client.resource_groups.create_or_update(
        RESOURCE_GROUP_NAME, {"location": location})

    logging.info("Resource Group created" + result.name + " in " + result.location)

    logging.info("Creating Virtual network")



    VNET_NAME = "vnet-" + vm_name

    poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
                                                                    VNET_NAME,
                                                                    {
                                                                        "location": location,
                                                                        "address_space": {
                                                                            "address_prefixes": ["192.0.0.0/16"]
                                                                        }
                                                                    }
                                                                    )

    vnet_result = poller.result()

    logging.info("Creation completed")


    logging.info("Creating Subnet")

    SUBNET_NAME = "subnet-" + vm_name

    poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME,
                                                        VNET_NAME, SUBNET_NAME, {
                                                            "address_prefix": "192.0.0.0/24"}
                                                        )
    subnet_result = poller.result()

    logging.info("Creation completed")


    logging.info("Creating IPs")

    IP_NAME = "ip-" + vm_name

    poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME, IP_NAME, {
        "location": location,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4"
    })

    ip_address_result = poller.result()

    logging.info("Creation comepleted")

    logging.info("Creating network security group")

    NSG_NAME = "nsg-" + vm_name


    parameters = NetworkSecurityGroup()
    parameters.location = location
    parameters.security_rules = [SecurityRule(
        protocol='Tcp',
        access='Allow',
        direction='Inbound',
        description='Allow all ports',
        source_address_prefix='*',
        destination_address_prefix='*',
        source_port_range='*',
        destination_port_range='*',
        priority=110,
        name='PlatformManager')]

    poller = network_client.network_security_groups.begin_create_or_update(
        RESOURCE_GROUP_NAME, NSG_NAME, parameters)

    nsg_result = poller.result()

    logging.info("Creation completed")

    logging.info("Creating network interface card")

    NIC_NAME = "nic-" + vm_name
    IP_CONFIG_NAME = "ip-config-" + vm_name


    poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME, NIC_NAME, {
        "location": location,
        'network_security_group': {
            'id': nsg_result.id
        },
        "ip_configurations": [{
            "name": IP_CONFIG_NAME,
            "subnet": {"id": subnet_result.id},
            "public_ip_address": {"id": ip_address_result.id}

        }]
    })

    nic_result = poller.result()

    logging.info("Creation completed")

    Compute_client = ComputeManagementClient(
        credential, subscription_id)
    VM_NAME = vm_name
    logging.info(f"Provisioning {VM_NAME};")
    poller = Compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
                                                                    {
                                                                        "location": location,
                                                                        "storage_profile": {
                                                                            "imageReference": {
                                                                                "sku": "18.04-LTS",
                                                                                "publisher": "Canonical",
                                                                                "version": "latest",
                                                                                "offer": "UbuntuServer"
                                                                            }
                                                                        },
                                                                        "hardware_profile": {
                                                                            "vm_size": "Standard_DS1_v2"
                                                                        },
                                                                        "os_profile": {
                                                                            "computer_name": VM_NAME,
                                                                            "admin_username": username,
                                                                            "admin_password": password
                                                                        },
                                                                        "network_profile": {
                                                                            "network_interfaces": [{
                                                                                "id": nic_result.id,
                                                                            }]
                                                                        }
                                                                    })
    vm_result = poller.result()
    cmd = "az vm list-ip-addresses -n " + vm_name + \
        " --query [0].virtualMachine.network.publicIpAddresses[0].ipAddress -o tsv > out_file.txt"
    os.system(cmd)
    contents = ""
    with open("out_file.txt") as f:
        contents = f.read()
    logging.info(f" VM Provisioned {vm_result.name}")
    os.remove("out_file.txt")
    return contents[:-1]

def run():
    server_list = sys.argv[1]
    servers = json.loads(open(server_list).read())
    subscription_id = servers['subscription_id']
    if 'master' in servers:
        vm_name = servers['master']['user']
        username = servers['master']['user']
        password = servers['master']['pass']
        location = servers['master']['location']
        ip = create(subscription_id,vm_name,username,password,location)
        logging.info('Master IP: ' + ip)
        servers['master']['ip'] = ip
    
    for worker in servers['workers']:
        vm_name = worker['user']
        username = worker['user']
        password = worker['pass']
        location = worker['location']
        ip = create(subscription_id,vm_name,username,password,location)
        logging.info('Worker IP: ' + ip)
        worker['ip'] = ip
    
    with open(server_list, 'w') as f:
        json.dump(servers, f, indent=4)

if __name__ == "__main__":
    run()