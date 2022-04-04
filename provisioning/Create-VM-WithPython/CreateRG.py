from azure.mgmt.resource import ResourceManagementClient
import Config
import Location

Location

rg_client = ResourceManagementClient(Config.credential, Config.subscription_id)

RESOURCE_GROUP_NAME = "RG-" + Config.vm_name


result = rg_client.resource_groups.create_or_update(
    RESOURCE_GROUP_NAME, {"location": Location.LOCATION})
print(f"Provisioning resource group {result.name} in {result.location} ")
