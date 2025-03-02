import hmac
import hashlib
import base64
import time
import requests

# Function to get the current timestamp
def get_timestamp():
    return str(int(time.time() * 1000))

# Function to generate the signature
def generate_signature(secret_key, timestamp, method, request_path, body):
    pre_hash_string = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(secret_key.encode('utf-8'), pre_hash_string.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

# Hardcoded credentials for a single account
api_key = 'API_KEY'
secret_key = 'SECRET_KEY'
passphrase = 'PASSPHRASE'

# Function to get all positions
# for fetching demo future trades put "product_type='SUSDT-FUTURES', margin_coin='SUSDT'"

def get_all_positions(api_key, secret_key, passphrase, product_type='SUSDT-FUTURES', margin_coin='SUSDT'):
    base_url = 'https://api.bitget.com'
    
    # Construct the API endpoint and request path
    endpoint = f"/api/v2/mix/position/all-position?productType={product_type}&marginCoin={margin_coin}"
    url = base_url + endpoint
    timestamp = get_timestamp()
    method = 'GET'
    body = ''  # No body for GET request
    
    # Generate the signature for the request
    signature = generate_signature(secret_key, timestamp, method, endpoint, body)
    
    headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': signature,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': timestamp,
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    try:
        # Make the request to get all positions
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        # Print the response data
        print("All Positions Data:", data)
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all positions: {e}")

# Call the function for all positions (You can specify product type and margin coin if needed)
get_all_positions(api_key, secret_key, passphrase)
