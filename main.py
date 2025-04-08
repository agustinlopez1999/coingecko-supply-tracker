from datetime import datetime, timezone
import requests, json

api_url = "https://api.coingecko.com/api/v3/coins/"

def get_main_cripto_data_from_api(cripto_name):
    url = f"{api_url}/{cripto_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_x_days_cripto_data_from_api(cripto_name, days):
    url = f"{api_url}/{cripto_name}/market_chart?vs_currency=usd&days={days}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_oldest_available_market_data(cripto_name, max_days=365):
    old_data_from_api = get_x_days_cripto_data_from_api(cripto_name, max_days)

    if not old_data_from_api or "prices" not in old_data_from_api or not old_data_from_api["prices"]:
        return {
            "price_old": None,
            "market_cap_old": None,
            "circulating_supply_old": None,
            "days_since_old_data": None,
            "msg": "No historical data available"
        }
    else:
        #first timestamp
        timestamp_ms = old_data_from_api["prices"][0][0]
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        days_since_old_data = (now - timestamp).days

        #get old_data_from_api values
        #old_price
        old_price = old_data_from_api["prices"][0][1]

        #old_market_cap
        if old_data_from_api.get("market_caps") and old_data_from_api["market_caps"]:
            old_market_cap = old_data_from_api["market_caps"][0][1]
        else:
            old_market_cap = None

        #old_supply
        if old_price and old_market_cap:
            old_circulating_supply = old_market_cap / old_price
        else:
            old_circulating_supply = None

        return{
            "old_price": old_price,
            "old_market_cap": old_market_cap,
            "old_circulating_supply": old_circulating_supply,
            "days_since_old_data": days_since_old_data,
            "note": f"Oldest data is from {days_since_old_data} days ago"
        }


    
def build_cripto_summary(cripto_name):
    data_from_api = get_main_cripto_data_from_api(cripto_name)
    old_data_summary = get_oldest_available_market_data(cripto_name)
    if not data_from_api:
        return {"error":"No data available"}
    try:
        summary = {
            #name_data
            "id":data_from_api["id"],
            "name": data_from_api["name"],
            "symbol": data_from_api["symbol"],

            #market_data
            "price": data_from_api["market_data"]["current_price"]["usd"],
            "market_cap": data_from_api["market_data"]["market_cap"]["usd"],
            "market_cap_rank": data_from_api["market_cap_rank"],

            #supply
            "circulating_supply": data_from_api["market_data"]["circulating_supply"],
            "max_supply": data_from_api["market_data"]["max_supply"],
            "max_supply_is_infinity": data_from_api["market_data"]["max_supply_infinite"],

            #ath
            "ath": data_from_api["market_data"]["ath"]["usd"],
            "ath_change_percentage": data_from_api["market_data"]["ath_change_percentage"]["usd"],
            "ath_date": data_from_api["market_data"]["ath_date"]["usd"],

            #price_change_percentage
            "price_change_percentage_24h": data_from_api["market_data"]["price_change_percentage_24h"],
            "price_change_percentage_7d": data_from_api["market_data"]["price_change_percentage_7d"],
            "price_change_percentage_14d": data_from_api["market_data"]["price_change_percentage_14d"],
            "price_change_percentage_30d": data_from_api["market_data"]["price_change_percentage_30d"],
            "price_change_percentage_60d": data_from_api["market_data"]["price_change_percentage_60d"],
            "price_change_percentage_1y": data_from_api["market_data"]["price_change_percentage_1y"],

            #images
            "image_thumb": data_from_api["image"]["thumb"],
            "image_small": data_from_api["image"]["small"],
            "image_large": data_from_api["image"]["large"],

            #old_data
            "old_price": old_data_summary["old_price"],
            "old_market_cap": old_data_summary["old_market_cap"],
            "old_circulating_supply": old_data_summary["old_circulating_supply"],
            "days_since_old_data": old_data_summary["days_since_old_data"],
            "circulating_emission_percentage": ((data_from_api["market_data"]["circulating_supply"] - old_data_summary["old_circulating_supply"])/ old_data_summary["old_circulating_supply"]) * 100,
            "historical_note": old_data_summary["note"],

        }
        return summary
    except Exception as error:
        return {"error": str(error)}

if __name__ == "__main__":
    result = build_cripto_summary("worldcoin-wld") #choose desired crypto
    print(json.dumps(result, indent=4))
    