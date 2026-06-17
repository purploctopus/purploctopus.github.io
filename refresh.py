import json
import urllib.request
import sys

# Upgraded to active v2.3.0 endpoint with the new plural /launches/ path
API_URL = "https://thespacedevs.com"

try:
    print("Fetching raw data from Launch Library 2 (v2.3.0)...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0 SpaceAppDataSync'})
    
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        raw_body = response.read().decode('utf-8')
        
    # Attempt to parse the retrieved content
    try:
        raw_data = json.loads(raw_body)
    except json.JSONDecodeError as json_err:
        print(f"\n❌ CRITICAL: Server did not return valid JSON! Status Code: {status_code}")
        print("--- START OF SERVER RESPONSE PREVIEW ---")
        print(raw_body[:500])  # Prints the first 500 characters of the error message to debug
        print("--- END OF SERVER RESPONSE PREVIEW ---")
        sys.exit(1)

    optimized_launches = []
    
    # Process the verified data structure safely
    for launch in raw_data.get('results', []):
        # Look for video elements natively inside the updated array structure
        vid_list = launch.get("vidURLs", [])
        video_url = vid_list[0].get("url") if isinstance(vid_list, list) and len(vid_list) > 0 else None
        
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # The scheduled date string
            "pad_name": launch.get("pad", {}).get("name"),
            "location": launch.get("pad", {}).get("location", {}).get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"✅ Success! Successfully compiled {len(optimized_launches)} launches into launches.json.")

except Exception as e:
    print(f"❌ General script error: {e}")
    sys.exit(1)
