import requests
import json
from influxdb import InfluxDBClient
from datetime import datetime
import dotenv
import os

dotenv.load_dotenv(".env")
PASSWORD = os.environ["PASSWORD"]
USERNAME = os.environ["USERNAME"]
email = "prism@global.corp.sap"


def ali_cf_oauth_token():
    url = "https://uaa.cf.canaryac.vlab-sapcloudplatformdev.cn/oauth/token"

    payload = "grant_type=password&client_id=cf&client_secret=&username=prism@global.corp.sap&password=Prisminfra529#5"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=MTA3YTRmMWItZTdjMy00MjMyLTgxNzItMWE0YWJmMGRmYjA4; __VCAP_ID__=6dab327d-d943-477a-44e8-187fab5d3140'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response.raise_for_status()

    ali_token = response.json()

    return ali_token["access_token"]


def ali_cpi_prod_version():
    url = "https://api.cf.canaryac.vlab-sapcloudplatformdev.cn/v3/apps?page=1&per_page=1000&space_guids=99e7eb42-3867-4bf1-9e92-6b43fe09b24f&names=it-co"

    payload = {}
    headers = {
        'Authorization': f'Bearer {ali_cf_oauth_token()}'
    }

    co_response = (requests.request("GET", url, headers=headers, data=payload)).json()
    co_guid = co_response["resources"][0]["guid"]

    url = f"https://api.cf.canaryac.vlab-sapcloudplatformdev.cn/v3/apps/{co_guid}/environment_variables"

    payload = {}
    headers = {
        'Authorization': f'Bearer {ali_cf_oauth_token()}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    cpi_product_version = response.json()["var"]["CPI_PRODUCT_VERSION"]

    return cpi_product_version


def ali_push_app_info():
    dev_client = InfluxDBClient('hci-rit-prism-sel.cpis.c.eu-de-2.cloud.sap', 8086, 'arpdb')
    dev_client.switch_database('arpdb')

    app_list = ["it-co", "it-trm", "it-gb", "it-app", "it-rootwebapp", "it-design-service", "it-app-prov", "it-km-rest",
                "it-op-rest", "it-op-odata", "it-op-consumer", "it-is-app-prov-route", "it-runtime-api", "it-tpm",
                "it-tlm-service", "it-op-consumer-b2b", "it-op-jobs", "it-op-jobs-archiving",
                "it-op-odata-batch-router",
                "it-op-static", "it-op-static-b2b"]

    for app in app_list:
        url = f"https://api.cf.canaryac.vlab-sapcloudplatformdev.cn/v3/apps?page=1&per_page=1000&space_guids" \
              f"=99e7eb42-3867-4bf1-9e92-6b43fe09b24f&names={app}"

        payload = {}
        headers = {
            'Authorization': f'Bearer {ali_cf_oauth_token()}'
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
                        "IAAS": "ALI-IAT",
                        "Product_Version": f"{ali_cpi_prod_version()} - {datetime.now().date()}"
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
                print(f"{app_name} Data Insertion success")
                pass
            else:
                print(f"{app_name} Dev-Data Insertion Failed")
                print(all_app_info)


def main():
    ali_cf_oauth_token()
    ali_cpi_prod_version()
    ali_push_app_info()


if __name__ == "__main__":
    main()
