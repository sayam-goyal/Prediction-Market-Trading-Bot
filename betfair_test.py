import betfairlightweight
import requests

# # Define the endpoint and payload
# url = "https://identitysso.betfair.com/api/login"
# headers = {
#     "Accept": "application/json",
#     "X-Application": "<AppKey>"
# }
# data = {
#     "username": "<username>",
#     "password": "<password>"
# }

# # Make the POST request
# response = requests.post(url, headers=headers, data=data, verify=False)

# # Print the response
# print(f"Status Code: {response.status_code}")
# print(f"Response Body: {response.text}")

trading = betfairlightweight.APIClient(
    "coolspam125@gmail.com", "in2us2nj@B", app_key="X0301DoEHpxFGS60"
)
trading.login_interactive()
print(
    trading.historic.get_collection_options(
        sport="Other Sports",
        plan="Basic Plan",
        from_day=1,
        from_month=1,
        from_year=2024,
        to_day=30,
        to_month=12,
        to_year=2024,
        countries_collection=["USA"]
    )
)
