import json
import os
import sys

print("--- STARTING ROCKETLAUNCH.LIVE DATA CONVERTER ---")

if not os.path.exists("raw_launches.json"):
    print("❌ CRITICAL ERROR: Raw download file is missing.")
    sys.exit(1)

try:
    with open("raw_launches.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    optimized_launches = []
    # RocketLaunch.Live encapsulates its array within the 'result' field
    results = raw_data.get('result', [])
    
    print(f"Successfully loaded {len(results)} global launches. Formatting...")
    
    for launch in results:
        # Extract location structures safely
        pad_info = launch.get("pad", {})
        location_info = pad_info.get("location", {})
        
        # Pull direct livestream video links if they are active
        video_url = launch.get("media", [{}])[0].get("url") if launch.get("media") else None
        
        clean_item = {
            "id": str(launch.get("id")),
            "name": launch.get("name"),
            "date_utc": launch.get("win_open"),  # The ISO UTC date window opening timestamp
            "pad_name": pad_info.get("name"),
            "location": f"{location_info.get('name')}, {location_info.get('country')}",
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Save the polished JSON package for your iOS app
    with open("launches.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=4)
        
    if os.path.exists("raw_launches.json"):
        os.remove("raw_launches.json")
        
    print(f"✅ SUCCESS! Compiled {len(optimized_launches)} global launches into launches.json.")

except Exception as e:
    print(f"❌ Processing error while building JSON schema: {e}")
    sys.exit(1)

