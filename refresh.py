import json
import os
import sys
from datetime import datetime

print("--- STARTING MONTHLY GLOBAL DATA CONVERTER ---")

if not os.path.exists("raw_launches.json"):
    print("❌ CRITICAL ERROR: Raw download file is missing.")
    sys.exit(1)

try:
    with open("raw_launches.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    optimized_launches = []
    results = raw_data.get('result', [])
    
    print(f"Loaded {len(results)} total upcoming listings from the feed. Parsing timeline...")
    
    for launch in results:
        pad_info = launch.get("pad", {})
        location_info = pad_info.get("location", {})
        
        # Pull direct livestream video links if they are active
        video_url = launch.get("media", [{}]).get("url") if launch.get("media") else None
        
        # Format dates securely
        date_raw = launch.get("win_open")
        
        clean_item = {
            "id": str(launch.get("id")),
            "name": launch.get("name"),
            "date_utc": date_raw,  # ISO UTC string or null if date TBD
            "pad_name": pad_info.get("name"),
            "location": f"{location_info.get('name')}, {location_info.get('country')}",
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Save the polished JSON calendar package for your iOS app
    with open("launches.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=4)
        
    if os.path.exists("raw_launches.json"):
        os.remove("raw_launches.json")
        
    print(f"✅ SUCCESS! Created launches.json with a comprehensive launch schedule.")

except Exception as e:
    print(f"❌ Processing error while building monthly JSON schema: {e}")
    sys.exit(1)
