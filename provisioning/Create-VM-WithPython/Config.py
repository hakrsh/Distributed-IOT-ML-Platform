from azure.identity import AzureCliCredential
import os


credential = AzureCliCredential()

subscription_id = os.environ["Azure_Sub_Id"] = "33f4f7cd-44fe-4cbe-b482-a5bce2fe048b"
vm_name = "VM2"
