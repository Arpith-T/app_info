import requests
import json
from influxdb import InfluxDBClient
from datetime import datetime

space_guid = "e4451758-664a-4a4e-8edd-ceeef7204488"
azure_url = "https://api.cf.eu20.hana.ondemand.com/v3/apps"


def azure_cf_oauth_token():
    import requests

    url = "https://uaa.cf.eu20.hana.ondemand.com/oauth/token"

    payload = "grant_type=password&client_id=cf&client_secret=&username=prism@global.corp.sap&password=Prisminfra529#5"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=ZGU0ZjIyMGUtNjk3My00ZDUxLTgwYWQtMTEyMGE2YjFjNTJh; __VCAP_ID__=9830a429-444f-42d7-4de1-ac02568eed3d'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    azure_token = response.json()

    return azure_token["access_token"]

# Influx
dev_client = InfluxDBClient('hci-rit-prism-sel.cpis.c.eu-de-2.cloud.sap', 8086, 'arpdb')
dev_client.switch_database('arpdb')

app_list = ["it-co", "it-trm", "it-gb", "it-app", "it-rootwebapp", "it-design-service", "it-app-prov", "it-km-rest",
            "it-op-rest", "it-op-odata", "it-op-consumer", "it-is-app-prov-route", "it-runtime-api", "it-tpm",
            "it-tlm-service", "it-op-consumer-b2b", "it-op-jobs", "it-op-jobs-archiving", "it-op-odata-batch-router",
            "it-op-static", "it-op-static-b2b"]


def cpi_prod_version():
    url = f"{azure_url}?page=1&per_page=1000&space_guids={space_guid}&names=it-co"

    payload = {}
    headers = {
        'Authorization': f'Bearer {azure_cf_oauth_token()}'
    }

    co_response = (requests.request("GET", url, headers=headers, data=payload)).json()
    co_guid = co_response["resources"][0]["guid"]

    url = f"{azure_url}/{co_guid}/environment_variables"

    payload = {}
    headers = {
        'Authorization': f'Bearer {azure_cf_oauth_token()}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    cpi_product_version = response.json()["var"]["CPI_PRODUCT_VERSION"]

    return cpi_product_version


for app in app_list:
    url = f"https://{azure_url}?page=1&per_page=1000&space_guids={space_guid}&names={app}"

    payload = {}
    headers = {
        'Authorization': f'Bearer {azure_cf_oauth_token()}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    app_info = response.json()

    # print(app_info)

    for application in app_info["resources"]:
        # print(application)
        app_name = app_info["resources"][0]["name"]
        app_state = app_info["resources"][0]["state"]
        app_version = app_info["resources"][0]["metadata"]["annotations"]["mta_version"]
        app_updated_at = app_info["resources"][0]["updated_at"]
        app_guid = app_info["resources"][0]["guid"]

        # print(f"App->{app_name}\nStatus-{app_state}\nApp-Version-{app_version}\nUpdatedOn-{app_updated_at}\nGUID-{app_guid}\n\n")

        all_app_info = [
            {
                "measurement": "MTMS_INFO",
                "tags": {
                    "IAAS": "Azure",
                    "Product_Version": f"{cpi_prod_version()} - {datetime.now().date()}"
                },
                "fields": {
                    "Microservice": app_name,
                    "Status": app_state,
                    "Version": app_version,
                    "UpdatedOn": app_updated_at,
                    "GUID": app_guid
                }
            }
        ]
        # print(all_app_info)
        if dev_client.write_points(all_app_info, protocol='json'):
            print("Data Insertion success")
            pass
        else:
            print("Dev-Data Insertion Failed")
            print(all_app_info)
