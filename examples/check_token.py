from ensembledata.api import EDClient
from datetime import datetime

# Your API token
API_TOKEN = "f5Kbwj1Kz03O2GXV"

def check_token_status():
    client = EDClient(API_TOKEN)
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Check today's usage
        usage = client.customer.get_usage(date=today)
        print(f"\nToday's Usage ({today}):")
        print(f"Units charged: {usage.units_charged}")
        print(f"Usage data: {usage.data}")
        # Get usage history for the last 7 days
        history = client.customer.get_usage_history(days=7)
        print(f"\nLast 7 days history:")
        print(f"Units charged: {history.units_charged}")
        print(f"History data: {history.data}")
        
    except Exception as e:
        print(f"Error checking token status: {str(e)}")

if __name__ == "__main__":
    check_token_status()