import json
import urllib.request
import sys

# Explicitly requesting the exact json structure directly inside the web path
API_URL = "https://thespacedevs.com"

try:
    print("Fetching raw data from Launch Library 2 (v2.3.0)...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SpaceTrackerApp/1.0'
    }
    
    req = urllib.request.Request(API_URL, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        raw_body = response.read().decode('utf-8')
        
    try:
        raw_data = json.loads(raw_body)
    except json.JSONDecodeError as json_err:
        print(f"\n❌ CRITICAL: Server did not return valid JSON! Status Code: {status_code}")
        print("--- START OF SERVER RESPONSE PREVIEW ---")
        print(raw_body[:500])
        print("--- END OF SERVER RESPONSE PREVIEW ---")
        sys.exit(1)

    optimized_launches = []
    
    # Process the data array structure safely
    for launch in raw_data.get('results', []):
        # Locate the stream link cleanly if it exists in the feed elements
        vid_urls = launch.get("vid_urls", [])
        video_url = None
        if isinstance(vid_urls, list) and len(vid_urls) > 0:
            first_vid = vid_urls[0]
            video_url = first_vid.get("url") if isinstance(first_vid, dict) else first_vid
            
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # Scheduled launch date time window
            "pad_name": launch.get("pad", {}).get("name"),
            "location": launch.get("pad", {}).get("location", {}).get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"✅ Success! Compiled {len(optimized_launches)} launches into launches.json.")

except Exception as e:
    print(f"❌ General script error: {e}")
    sys.exit(1)
