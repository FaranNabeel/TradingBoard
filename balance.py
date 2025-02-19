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
api_key = 'API-KEY-HERE'
secret_key = 'SECRET-KEYT-HERE'
passphrase = 'PASSPHRASE-HERE'

# Function to fetch balance and positions for a single account
def fetch_futures_balance(api_key, secret_key, passphrase, account_num):
    base_url = 'https://api.bitget.com'
    
    # Fetch account balance
    balance_endpoint = '/api/v2/account/all-account-balance'
    balance_url = base_url + balance_endpoint
    timestamp = get_timestamp()
    balance_method = 'GET'
    balance_body = ''
    balance_signature = generate_signature(secret_key, timestamp, balance_method, balance_endpoint, balance_body)
    
    balance_headers = {
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': balance_signature,
        'ACCESS-PASSPHRASE': passphrase,
        'ACCESS-TIMESTAMP': timestamp,
        'locale': 'en-US',
        'Content-Type': 'application/json',
    }
    
    try:
        # Make the request for balance
        balance_response = requests.get(balance_url, headers=balance_headers)
        balance_response.raise_for_status()  # Raise an error for bad status codes
        data = balance_response.json()
        
        # Print the entire balance response to inspect the structure
        print("Balance Response:", data)

        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching account {account_num} balances: {e}")

# Call the function for a single account (e.g., Account 1)
fetch_futures_balance(api_key, secret_key, passphrase, 1)
