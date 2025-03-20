import requests

def lookup(symbols):
    if isinstance(symbols, str):
        symbols = [symbols]

    api_key = "a74c1d6a9bfc48a096826ab16608dd72"
    stock_data = []

    for symbol in symbols:
        if symbol.startswith("^") or "," in symbol:
            continue

        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={api_key}"

        try:
            response = requests.get(url).json()
           

            if "code" in response:
                continue

            price = response.get("close")
            if price is not None:
                price = round(float(price), 2)

            stock_data.append({
                "symbol": symbol.upper(),
                "price": price,
                "company": response.get("name")
            })

        except requests.RequestException as e:
            print(f"Request error fetching data: {e}")
        except KeyError as e:
            print(f"KeyError fetching data: {e}")
        except Exception as e:
            print(f"Error fetching data: {e}")

    if len(stock_data) == 1:
        return stock_data[0]
    else:
        return stock_data
