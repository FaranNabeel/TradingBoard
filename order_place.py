import requests
import time
import hmac
import hashlib
import base64
import json
import sys

# API Configuration (Replace with your credentials)
API_KEY = "API_key"
SECRET_KEY = "SECRET_KEY"
PASSPHRASE = "PASSPHRASE"

# Order Parameters (Modify according to your needs)
order_params = {
    "symbol": "SETHSUSDT",
    "productType": "SUSDT-FUTURES",
    "marginMode": "isolated",
    "marginCoin": "SUSDT",
    "size": "0.1",
    "price": "2766",
    "side": "sell",
    "tradeSide": "open",
    "orderType": "market",
    "force": "gtc",
    "clientOid": str(int(time.time() * 1000))  # Generate unique client order ID
}

def generate_signature(secret, timestamp, method, request_path, body):
    message = str(timestamp) + method + request_path + body
    mac = hmac.new(bytes(secret, 'utf-8'), bytes(message, 'utf-8'), digestmod=hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

def place_order():
    # API Endpoint
    url = "https://api.bitget.com/api/v2/mix/order/place-order"
    
    # Generate timestamp
    timestamp = int(time.time() * 1000)
    
    # Create JSON body
    json_body = str(order_params).replace("'", '"')
    
    # Generate signature
    signature = generate_signature(
        secret=SECRET_KEY,
        timestamp=timestamp,
        method="POST",
        request_path="/api/v2/mix/order/place-order",
        body=json_body
    )
    
    # Set request headers
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": str(timestamp),
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "locale": "en-US",
        "Content-Type": "application/json"
    }
    
    # Send POST request
    response = requests.post(url, headers=headers, json=order_params)
    
    return response.json()

if __name__ == "__main__":
    try:
        result = place_order()
        print("Order Response:", repr(result))  # Print the result using repr() to handle encoding
        
        # Alternatively, write to stdout in UTF-8 encoding
        sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
    except Exception as e:
        print("Error placing order:", str(e))
