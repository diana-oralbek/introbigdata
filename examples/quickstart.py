import os

from ensembledata.api import EDClient


def main() -> None:
    # Option A (recommended): set ENSEMBLEDATA_API_TOKEN in your environment
    #   export ENSEMBLEDATA_API_TOKEN="YOUR_TOKEN"
    #   python examples/quickstart.py
    # Option B: paste your token below and run the script
    pasted_token = "f5Kbwj1Kz03O2GXV"

    token = os.environ.get("ENSEMBLEDATA_API_TOKEN", pasted_token)
    if not token or token == "PASTE_YOUR_TOKEN_HERE":
        raise SystemExit(
            "No API token provided. Set ENSEMBLEDATA_API_TOKEN or paste it in pasted_token."
        )

    client = EDClient(token)

    # You're ready to go. Uncomment an example call below to try it out.
    # Example (may consume units on your account):
    # result = client.tiktok.user_info_from_username(username="daviddobrik")
    # print("Data:", result.data)
    # print("Units charged:", result.units_charged)

    print("EDClient initialized successfully.")


if __name__ == "__main__":
    main()


