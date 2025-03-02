import hmac
import hashlib
import base64
import time
import requests
import json

# Function to get the current timestamp
def get_timestamp():
    return str(int(time.time() * 1000))

# Function to generate the signature
def generate_signature(secret_key, timestamp, method, request_path, body):
    pre_hash_string = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(secret_key.encode('utf-8'), pre_hash_string.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

# Function to close a position
def close_position(api_key, secret_key, passphrase, symbol, product_type, hold_side):
    base_url = 'https://api.bitget.com'  # URL for production trading (replace with testnet URL for demo)
    endpoint = '/api/v2/mix/order/close-positions'
    url = base_url + endpoint
    timestamp = get_timestamp()
    method = 'POST'
    
    # Prepare the data for the close position request
    position_data = {
        'symbol': symbol,
        'productType': product_type,
        'holdSide': hold_side,  # 'long' or 'short'
    }

    # Convert position data to JSON
    body = json.dumps(position_data)
    
    # Generate the signature for the request
    signature = generate_signature(secret_key, timestamp, method, endpoint, body)

    headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': signature,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': timestamp,
        'locale': 'en-US',  # Change to 'en-US' if necessary
        'Content-Type': 'application/json',
    }

    try:
        # Make the POST request to close the position
        response = requests.post(url, headers=headers, data=body)
        
        # Debugging: Print the full response
        print("Response Status Code:", response.status_code)
        
        # Printing the response using json.dumps with ensure_ascii=False to handle non-ASCII characters
        response_text = response.text
        print("Response Text:", json.dumps(json.loads(response_text), ensure_ascii=False))  # Handle non-ASCII chars correctly
        
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        # Print the response data (position closure details)
        print("Close Position Result:", data)
    except requests.exceptions.RequestException as e:
        print(f"Error closing position: {e}")

# Hardcoded credentials for a single account
api_key = 'api-key'
secret_key = 'secret-key'
passphrase = 'passphrase'

# Hardcoded details for the close position request
symbol = 'SETHSUSDT'              # Symbol of the trading pair (e.g., BTCUSDT)
product_type = 'SUSDT-FUTURES'   # The product type (e.g., USDT-FUTURES)
hold_side = 'short'              # Hold side ('long' or 'short')

# Close the position
close_position(api_key, secret_key, passphrase, symbol, product_type, hold_side)
