import GetObjectNetwork
import CreateRG
import Location
import Config

network_client = GetObjectNetwork.NetworkManagementClient(
    Config.credential, Config.subscription_id)
IP_NAME = "ip-" + Config.vm_name

poller = network_client.public_ip_addresses.begin_create_or_update(CreateRG.RESOURCE_GROUP_NAME, IP_NAME, {
    "location": Location.LOCATION,
    "sku": {"name": "Standard"},
    "public_ip_allocation_method": "Static",
    "public_ip_address_version": "IPV4"
})

ip_address_result = poller.result()
