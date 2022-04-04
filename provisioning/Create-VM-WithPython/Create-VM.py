import logging
from azure.mgmt.compute import ComputeManagementClient
import Config
import Location
import CreateRG
import CreateSubnet
import CreateIpAdresse
import CreateNSG
import CreateNiC
import CreateVnet
import os


print(f"Starting ...")


CreateRG

CreateVnet

CreateSubnet

CreateIpAdresse

CreateNSG

CreateNiC


Compute_client = ComputeManagementClient(
    Config.credential, Config.subscription_id)
VM_NAME = Config.vm_name
Username = "hackathon2"
PASSWORD = "Hackathon@2022"

print(f"Provisioning {VM_NAME};")

poller = Compute_client.virtual_machines.begin_create_or_update(CreateRG.RESOURCE_GROUP_NAME, VM_NAME,
                                                                {
                                                                    "location": Location.LOCATION,
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
                                                                        "admin_username": Username,
                                                                        "admin_password": PASSWORD
                                                                    },
                                                                    "network_profile": {
                                                                        "network_interfaces": [{
                                                                            "id": CreateNiC.nic_result.id,
                                                                        }]
                                                                    }
                                                                })
vm_result = poller.result()

# print(vm_result)

cmd = "az vm list-ip-addresses -n " + Config.vm_name + \
    " --query [0].virtualMachine.network.publicIpAddresses[0].ipAddress -o tsv > out_file.txt"
os.system(cmd)
contents = ""
with open("out_file.txt") as f:
    contents = f.read()


print(f" VM Provisioned {vm_result.name}")

print("IP ->", contents[:-1])
