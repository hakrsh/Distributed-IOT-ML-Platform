import GetObjectNetwork
import CreateRG
import CreateVnet
import Config

network_client = GetObjectNetwork.NetworkManagementClient(
    Config.credential, Config.subscription_id)
SUBNET_NAME = "subnet-" + Config.vm_name

poller = network_client.subnets.begin_create_or_update(CreateRG.RESOURCE_GROUP_NAME,
                                                       CreateVnet.VNET_NAME, SUBNET_NAME, {
                                                           "address_prefix": "192.0.0.0/24"}
                                                       )
subnet_result = poller.result()
