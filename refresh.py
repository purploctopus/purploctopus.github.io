import json
import urllib.request
import sys

# Note the strict trailing slashes before the question marks—crucial for Django APIs!
SANDBOX_URL = "https://thespacedevs.com"
PRODUCTION_URL = "https://thespacedevs.com"

def fetch_launches(url):
    print(f"🚀 Attempting to connect directly to: {url}")
    try:
        headers = {
            'User-Agent': 'SpaceTrackerApp/1.0 (Language=Python; Developer=purploctopus)',
            'Accept': 'application/json'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            final_url = response.geturl()
            status_code = response.getcode()
            
            # If the server redirected us away to the home page website, catch it
            if "thespacedevs.com" in final_url and "launches" not in final_url:
                print(f"⚠️ Server redirected to a non-API webpage: {final_url}")
                return None
                
            raw_body = response.read().decode('utf-8')
            
        if raw_body.strip().startswith("<!DOCTYPE html>"):
            print("⚠️ Server returned an HTML web view instead of JSON.")
            return None
            
        return json.loads(raw_body)
        
    except Exception as e:
        print(f"⚠️ Network connection failed for this URL: {e}")
        return None

# --- Core Logic ---
print("--- STARTING DATA FETCH PIPELINE ---")

# Step 1: Try the standard Dev Sandbox link
raw_data = fetch_launches(SANDBOX_URL)

# Step 2: If the Sandbox failed, try the Production live feed
if raw_data is None:
    print("🔄 Dev Sandbox link rejected. Switching to primary live stream...")
    raw_data = fetch_launches(PRODUCTION_URL)

# Step 3: If both failed, stop and warn us
if raw_data is None:
    print("❌ CRITICAL: Both server streams failed to return valid data layouts.")
    sys.exit(1)

try:
    optimized_launches = []
    
    # Extract entries safely from the JSON array
    for launch in raw_data.get('results', []):
        # Safely parse out the video URLs from the updated v2.3.0 structure
        vid_urls = launch.get("vid_urls", [])
        video_url = None
        if isinstance(vid_urls, list) and len(vid_urls) > 0:
            first_vid = vid_urls[0]
            video_url = first_vid.get("url") if isinstance(first_vid, dict) else first_vid
            
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),
            "pad_name": launch.get("pad", {}).get("name"),
            "location": launch.get("pad", {}).get("location", {}).get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"\n✅ SUCCESS! Generated launches.json with {len(optimized_launches)} space launches.")

except Exception as e:
    print(f"❌ Processing error while building JSON structure: {e}")
    sys.exit(1)

