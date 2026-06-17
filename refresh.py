import json
import urllib.request
import sys

# Open, unblocked endpoint that welcomes GitHub Actions runners
API_URL = "https://spacexdata.com"

print("--- STARTING OPEN DATA FETCH PIPELINE ---")
print(f"Connecting to: {API_URL}")

try:
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'SpaceTrackerApp/1.0'})
    
    with urllib.request.urlopen(req, timeout=15) as response:
        raw_body = response.read().decode('utf-8')
        
    raw_data = json.loads(raw_body)
    optimized_launches = []
    
    # Process up to 20 upcoming launches into your application schema
    for launch in raw_data[:20]:
        links = launch.get("links", {})
        # Map out the livestream video url cleanly
        video_url = links.get("webcast")
        
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("date_utc"),  # ISO 8601 UTC timestamp format
            "pad_name": "SLC-40" if launch.get("launchpad") == "5e9e4501f3fe4f4ba8566747" else "LC-39A",
            "location": "Cape Canaveral, FL, USA",
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Write directly to your local file path
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"✅ SUCCESS! Created launches.json with {len(optimized_launches)} upcoming space flights.")

except Exception as e:
    print(f"❌ Script failed: {e}")
    sys.exit(1)

