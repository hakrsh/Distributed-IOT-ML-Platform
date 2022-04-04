import GetObjectNetwork
import CreateRG
import Location
from azure.mgmt.network.models import NetworkSecurityGroup
from azure.mgmt.network.models import SecurityRule
import Config

network_client = GetObjectNetwork.NetworkManagementClient(
    Config.credential, Config.subscription_id)
NSG_NAME = "nsg-" + Config.vm_name


parameters = NetworkSecurityGroup()
parameters.location = Location.LOCATION
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
    CreateRG.RESOURCE_GROUP_NAME, NSG_NAME, parameters)

nsg_result = poller.result()
