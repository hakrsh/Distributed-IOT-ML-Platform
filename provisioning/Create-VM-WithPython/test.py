from az.cli import az
import os
import sys
# output = az("vm list-ip-addresses -g RG-VM1 -n VM1")

# print(output)
# # print(output.find("publicIps"))


# cmd = "az vm list-ip-addresses -g RG-VM1 -n VM1 > out_file.txt"
cmd = "az vm list-ip-addresses -n VM1 --query [0].virtualMachine.network.publicIpAddresses[0].ipAddress -o tsv > out_file.txt"
os.system(cmd)
contents = ""
with open("out_file.txt") as f:
    contents = f.read()
# output = json.loads(output)
# for i in contents:
#     if i.find("ipAddress"):
#         print(i)
#     # print(i)

# print("***************")
# for i in contents:
#     if(i.find("ipAddress")):
#         print("bla")
#         print(i)
print(contents[:-1])
