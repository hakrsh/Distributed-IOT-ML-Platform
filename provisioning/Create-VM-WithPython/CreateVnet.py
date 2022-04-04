import GetObjectNetwork
import CreateRG
import Location
import Config

network_client = GetObjectNetwork.NetworkManagementClient(
    Config.credential, Config.subscription_id)

VNET_NAME = "vnet-" + Config.vm_name

poller = network_client.virtual_networks.begin_create_or_update(CreateRG.RESOURCE_GROUP_NAME,
                                                                VNET_NAME,
                                                                {
                                                                    "location": Location.LOCATION,
                                                                    "address_space": {
                                                                        "address_prefixes": ["192.0.0.0/16"]
                                                                    }
                                                                }
                                                                )

vnet_result = poller.result()
