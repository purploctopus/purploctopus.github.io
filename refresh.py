import json
import urllib.request
import sys

# The production-ready v2.3.0 endpoint path
API_URL = "https://thespacedevs.com"

try:
    print("Fetching raw data from Launch Library 2 (v2.3.0)...")
    
    # CRITICAL FIX: Explicitly request application/json so the server doesn't send HTML website data
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SpaceTrackerApp/1.0',
        'Accept': 'application/json'
    }
    
    req = urllib.request.Request(API_URL, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        raw_body = response.read().decode('utf-8')
        
    try:
        raw_data = json.loads(raw_body)
    except json.JSONDecodeError as json_err:
        print(f"\n❌ CRITICAL: Server still did not return valid JSON! Status Code: {status_code}")
        print("--- START OF SERVER RESPONSE PREVIEW ---")
        print(raw_body[:500])
        print("--- END OF SERVER RESPONSE PREVIEW ---")
        sys.exit(1)

    optimized_launches = []
    
    # Handle the structure returned by the v2.3.0 engine safely
    for launch in raw_data.get('results', []):
        vid_list = launch.get("vid_urls", launch.get("vidURLs", []))
        video_url = None
        if isinstance(vid_list, list) and len(vid_list) > 0:
            video_url = vid_list[0].get("url") if isinstance(vid_list[0], dict) else vid_list[0]
            
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # Scheduled launch date window
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
