import json
import urllib.request
import sys

# Primary developer sandbox and production fallback endpoints
SANDBOX_URL = "https://thespacedevs.com"
PRODUCTION_URL = "https://thespacedevs.com"

def fetch_launches(url, is_fallback=False):
    print(f"Connecting to: {url}")
    try:
        # CRITICAL FIX: Custom non-browser User-Agent ensures the server returns pure JSON text
        headers = {
            'User-Agent': 'SpaceTrackerLocalApp/1.0 (Contact: purploctopus; Automation Script)',
            'Accept': 'application/json'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.getcode()
            raw_body = response.read().decode('utf-8')
            
        # Verify if the response is actually an HTML page before decoding
        if raw_body.strip().startswith("<!DOCTYPE html>"):
            print("⚠️ Warning: Server returned an HTML web view instead of raw data data structures.")
            return None
            
        return json.loads(raw_body)
        
    except Exception as e:
        print(f"⚠️ Connection error on this endpoint: {e}")
        return None

# --- Main Execution Flow ---
raw_data = fetch_launches(SANDBOX_URL)

# Fallback mechanism if the sandbox endpoint is down or serving web pages
if raw_data is None:
    print("🔄 Switching to primary production data stream...")
    raw_data = fetch_launches(PRODUCTION_URL, is_fallback=True)

if raw_data is None:
    print("❌ CRITICAL: Both server links failed to return data. Aborting build process.")
    sys.exit(1)

try:
    optimized_launches = []
    
    # Process the v2.3.0 data fields securely
    for launch in raw_data.get('results', []):
        # Locate streaming content links securely under the updated 2.3.0 format rules
        vid_urls = launch.get("vid_urls", [])
        video_url = None
        if isinstance(vid_urls, list) and len(vid_urls) > 0:
            # Extract the string URL directly from the list item element
            first_entry = vid_urls[0]
            video_url = first_entry.get("url") if isinstance(first_entry, dict) else first_entry
            
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # Precise calendar date window string
            "pad_name": launch.get("pad", {}).get("name"),
            "location": launch.get("pad", {}).get("location", {}).get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Save processed payload file locally to disk
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"✅ Success! Compiled {len(optimized_launches)} upcoming global launches into launches.json.")

except Exception as e:
    print(f"❌ Processing engine failed: {e}")
    sys.exit(1)

