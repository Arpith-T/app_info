import requests
import json
from cf_oauth_token import aws_cf_oauth_token

token = aws_cf_oauth_token()


def app_process_info(guid, token):
    url = f"https://api.cf.sap.hana.ondemand.com/v3/apps/{guid}/processes"

    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    mtms_data = response.json()

    # mtms_data = app_info("1352f58c-8c84-4c0f-9657-bbc0e9bf621c")

    no_of_instances = mtms_data["resources"][0]["instances"]
    memory = mtms_data["resources"][0]["memory_in_mb"]
    disk_size = mtms_data["resources"][0]["disk_in_mb"]
    health_check_type = mtms_data["resources"][0]["health_check"]["type"]
    health_check_timeout = mtms_data["resources"][0]["health_check"]["data"]["timeout"]
    health_check_invocation_timeout = mtms_data["resources"][0]["health_check"]["data"]["invocation_timeout"]
    try:
        health_check_endpoint = mtms_data["resources"][0]["health_check"]["data"]["endpoint"]
    except KeyError as error_message:
        # print(f"The key {error_message} does not exist")
        return no_of_instances, memory, disk_size, health_check_type, health_check_timeout, health_check_invocation_timeout
    # else:
    #     print(
    #         f"\n{no_of_instances}\n{memory}\n{disk_size}\n{health_check_type}\n{health_check_timeout}\n{health_check_invocation_timeout}\n{health_check_endpoint}")

    else:
        return no_of_instances, memory, disk_size, health_check_type, health_check_timeout, health_check_invocation_timeout, health_check_endpoint





    # return no_of_instances, memory, disk_size, health_check_type, health_check_timeout, health_check_invocation_timeout, health_check_endpoint


# print(app_process_info("ff485dc3-5a35-4ba8-b676-ec313d6f36cf", token))
