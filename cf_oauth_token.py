import requests
import os
import dotenv

dotenv.load_dotenv(".env")
PASSWORD = os.environ["PASSWORD"]
USERNAME = os.environ["USERNAME"]
email = "prism@global.corp.sap"


def aws_cf_oauth_token():
    url = "https://uaa.cf.sap.hana.ondemand.com/oauth/token"

    payload = f"grant_type=password&client_id=cf&client_secret=&username={email}&password={PASSWORD}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=ZDc4OWZhNGYtNmZmMC00MDllLTg4MGEtY2NhMzAyM2YzMzYz; '
                  '__VCAP_ID__=6c9fa102-b148-485c-4f41-990197bba0cd '
    }

    return (requests.request("POST", url, headers=headers, data=payload)).json()["access_token"]

    # return response.json()["access_token"]

    # aws_access_token = aws_token["access_token"]

    # print(aws_access_token)

    # return aws_access_token


def azure_cf_oauth_token():
    import requests

    url = "https://uaa.cf.eu20.hana.ondemand.com/oauth/token"

    payload = f"grant_type=password&client_id=cf&client_secret=&username={email}&password={PASSWORD}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=ZGU0ZjIyMGUtNjk3My00ZDUxLTgwYWQtMTEyMGE2YjFjNTJh; '
                  '__VCAP_ID__=9830a429-444f-42d7-4de1-ac02568eed3d '
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    azure_token = response.json()

    # print(azure_token)

    return azure_token["access_token"]


# print(azure_cf_oauth_token())
