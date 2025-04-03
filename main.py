
from datetime import datetime, timezone
import requests

api_url = "https://api.coingecko.com/api/v3/coins/"

def get_cripto_data(name):
    url = f"{api_url}/{name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_supply_change_last_year(name, current_supply):
    url = f"{api_url}/{name}/market_chart?vs_currency=usd&days=365" 
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    try:
        market_cap_1y = data["market_caps"][0][1]
        price_1y = data["prices"][0][1]
        date_ts = data["prices"][0][0]
        date_1y = datetime.fromtimestamp(date_ts / 1000.0, tz=timezone.utc)
    except (IndexError, KeyError):
        return None

    supply_1y = market_cap_1y / price_1y
    change = ((current_supply - supply_1y) / supply_1y) * 100

    return {
        "date_1y": date_1y.date().isoformat(),
        "supply_1y": round(supply_1y, 2),
        "current_supply": round(current_supply, 2),
        "inflation": round(change, 2)
    }

def build_cripto_summary(cripto_name):
    cripto_info = get_cripto_data(cripto_name)
    if not cripto_info:
        return {"error": "No data found"}

    try:
        current_supply = cripto_info["market_data"]["circulating_supply"]
        total_supply = cripto_info["market_data"].get("total_supply")
        supply_emission = (current_supply * 100 / total_supply) if total_supply else None
        supply_1y = get_supply_change_last_year(cripto_name, current_supply)

        summary = {
            "name": cripto_info["name"],
            "symbol": cripto_info["symbol"],
            "price": cripto_info["market_data"]["current_price"]["usd"],
            "market_cap": cripto_info["market_data"]["market_cap"]["usd"],
            "current_supply": current_supply,
            "total_supply": total_supply,
            "supply_emission": round(supply_emission, 2) if supply_emission else None,
            "ath": cripto_info["market_data"]["ath"]["usd"],
            "ath_change": cripto_info["market_data"]["ath_change_percentage"]["usd"],
            "ath_date": cripto_info["market_data"]["ath_date"]["usd"],
            "supply_last_year": supply_1y
        }
        return summary
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    result = build_cripto_summary("bitcoin") #Choose cripto
    print(result)
