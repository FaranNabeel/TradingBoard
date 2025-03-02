import time
import hmac
import hashlib
import base64
import json
import requests

def get_timestamp():
    """
    Returns the current timestamp as a string (milliseconds).
    """
    return str(int(time.time() * 1000))

def generate_signature(secret_key, timestamp, method, request_path, body):
    pre_hash = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(secret_key.encode('utf-8'),
                         pre_hash.encode('utf-8'),
                         hashlib.sha256).digest()
    return base64.b64encode(signature).decode()

def place_tpsl_order(plan_type, trigger_price, execute_price, client_oid):
    
        # Replace these placeholders with your actual API credentials.
    api_key = "api-key"
    secret_key = "secret-key"
    passphrase = "passphrase"

    base_url = "https://api.bitget.com"
    request_path = "/api/v2/mix/order/place-tpsl-order"
    url = base_url + request_path
    method = "POST"

    # Build the payload.
    payload = {
        "marginCoin": "SUSDT",
        "productType": "Susdt-futures",
        "symbol": "sethsusdt",
        "planType": plan_type,          # "profit_plan" for take profit, "loss_plan" for stop loss
        "triggerPrice": trigger_price,  # Must be > mark price for profit_plan and < mark price for loss_plan
        "triggerType": "mark_price",    # Could also be "last_price" if desired
        "executePrice": execute_price,  # "0" means market execution
        "holdSide": "short",             # For a long position
        "size": "0.1",                    # Order size (quantity)
        "rangeRate": "",                # Optional; leave empty if not used
        "clientOid": client_oid         # Unique client order ID
    }

    # Convert payload to JSON string.
    body = json.dumps(payload)
    timestamp = get_timestamp()
    signature = generate_signature(secret_key, timestamp, method, request_path, body)

    # Set headers as required by Bitget.
    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": signature,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        response_json = response.json()
        print("Response JSON:")
        print(json.dumps(response_json, indent=2))
    except requests.exceptions.RequestException as e:
        print("Error placing TPSL order:", e)
        print("Response Text:", response.text)

if __name__ == "__main__":
    # Example 1: Place a Take Profit (Target) Order.
    # Since the current mark price is 2717.29, the target must be higher.
    print("Placing a Take Profit (Target) Order:")
    target_price = "2500"   # Use a value > 2717.29 (e.g., 2800)
    place_tpsl_order(plan_type="profit_plan", trigger_price=target_price, execute_price="0", client_oid="tp_order_001")
    
    # Example 2: Place a Stop Loss Order.
    # For a long position, the stop loss must be lower than the mark price.
    print("\nPlacing a Stop Loss Order:")
    stop_loss_price = "2800"   # Use a value < 2717.29 (e.g., 2650)
    place_tpsl_order(plan_type="loss_plan", trigger_price=stop_loss_price, execute_price="0", client_oid="sl_order_001")
