import json
import urllib.request

# The standard Launch Library 2 development endpoint (Free, no keys needed)
API_URL = "https://thespacedevs.com"

try:
    print("Fetching raw data from Launch Library 2...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_data = json.loads(response.read().decode())
    
    optimized_launches = []
    
    # Extract only the critical variables your app UI needs
    for launch in raw_data.get('results', []):
        # Look for video URLs securely
        vid_list = launch.get("vidURLs", [])
        video_url = vid_list[0].get("url") if vid_list else None
        
        clean_item = {
            "id": launch.get("id"),
            "name": launch.get("name"),
            "date_utc": launch.get("net"),  # Scheduled launch timestamp
            "pad_name": launch.get("pad", {}).get("name"),
            "location": launch.get("pad", {}).get("location", {}).get("name"),
            "video_url": video_url
        }
        optimized_launches.append(clean_item)
        
    output_payload = {"launches": optimized_launches}
    
    # Save file locally
    with open("launches.json", "w") as f:
        json.dump(output_payload, f, indent=4)
        
    print(f"Successfully processed {len(optimized_launches)} upcoming launches!")

except Exception as e:
    print(f"Error executing update: {e}")
    exit(1) # Signal failure to GitHub Actions if it crashes

