from ensembledata.api import EDClient, EDError

# Your API token
API_TOKEN = "d27oMjsSy7Lw4G8K"

def test_tiktok_call():
    client = EDClient(API_TOKEN)
    
    try:
        # Try a single hashtag search
        result = client.tiktok.hashtag_search(hashtag="test")
        print("Success! API call worked.")
        print(f"Units charged: {result.units_charged}")
        print(f"Number of posts: {len(result.data.get('data', []))}")
        
    except EDError as e:
        print(f"EnsembleData API Error:")
        print(f"Status code: {e.status_code}")
        print(f"Error detail: {e.detail}")
        print(f"Units charged: {e.units_charged}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    test_tiktok_call()