import json
import os
import sys

print("--- STARTING FILE PROCESSING ENGINE ---")

# Verify the network download step succeeded
if not os.path.exists("raw_launches.json"):
    print("❌ CRITICAL ERROR: The raw data download step failed to save the target file.")
    sys.exit(1)

try:
    with open("raw_launches.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    optimized_launches = []
    results = raw_data.get('results', [])
    
    print(f"Read {len(results)} global launches from source file. Processing...")
    
    # Process all global space missions (NASA, ESA, SpaceX, Rocket Lab, China, etc.)
    for launch in results:
        # Safe extraction of nested v2.3.0 fields
        pad = launch.get("pad", {})
        location = pad.get("location", {})
        
        # Safely drill down into the updated array structure for live stream videos
        vid_urls = launch.get("vid_urls", [])
        video_url = None
        if isinstance(vid_urls, list) and len(vid_urls) > 0:
            first_item = vid_urls[0]
            if isinstance(first_item, dict):
                video_url = first_item.get("url")
            else:
                video_url = str(first_item)
                
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # Absolute calendar launch timestamp
            "pad_name": pad.get("name"),
            "location": location.get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Output the optimized deployment file for the iOS application
    with open("launches.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=4)
        
    # Clean up the large raw staging file
    if os.path.exists("raw_launches.json"):
        os.remove("raw_launches.json")
        
    print(f"✅ SUCCESS! Created launches.json with {len(optimized_launches)} global space launches.")

except Exception as e:
    print(f"❌ Processing error while rebuilding JSON architecture: {e}")
    sys.exit(1)

