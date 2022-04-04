from azure.mgmt.network import NetworkManagementClient
import Config

# Obtenir l'objet de gestion pour le réseau
network_client = NetworkManagementClient(Config.credential, Config.subscription_id)
