import os
import re
import requests
import sys

# Configuration
BASE_URL = "https://galgos.inf.puc-rio.br/cvrplib/index.php/en/"
INSTANCES_URL = BASE_URL + "instances"
DOWNLOAD_INSTANCE_URL = BASE_URL + "download/instance/"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def get_instance_mapping():
    """
    Scrapes the CVRPLib instances page to map instance names to their download IDs.
    Returns a dict: {instance_name: instance_id}
    """
    print(f"Fetching instance list from {INSTANCES_URL}...")
    try:
        response = requests.get(INSTANCES_URL, timeout=30)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"Error fetching instances page: {e}")
        return {}

    mapping = {}
    lines = html_content.split('\n')
    
    # Simple parsing logic based on the Julia script and HTML structure
    # We look for lines containing "download/instance/{id}"
    # The name is usually in the subsequent lines or same block
    
    # Regex to find the download link: <a href=".../download/instance/123">
    # And then extract the name from the cell text.
    
    # A more robust way given the HTML might be unstructured text in lines:
    # The Julia script used a simple line-by-line lookahead.
    # Pattern: download/instance/(\d+)" followed by instance name on next line
    
    for i in range(len(lines) - 1):
        line = lines[i]
        match = re.search(r'download/instance/(\d+)"', line)
        if match:
            instance_id = match.group(1)
            # The name is likely in the next line or shortly after, inside <td> tags usually
            # The Julia script assumes it's on the next line.
            name_line = lines[i+1]
            # Strip HTML tags
            name = re.sub(r'<[^>]*>', '', name_line).strip()
            
            if name:
                mapping[name] = instance_id
                
    print(f"Found {len(mapping)} instances.")
    return mapping

def download_instance(name, instance_id):
    """Downloads a specific instance by ID."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    url = f"{DOWNLOAD_INSTANCE_URL}{instance_id}"
    file_path = os.path.join(DATA_DIR, f"{name}.vrp")
    
    if os.path.exists(file_path):
        # Check if it's a valid file (not empty or html error)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(100)
            if b"<!DOCTYPE html>" not in header and b"<html" not in header and os.path.getsize(file_path) > 100:
                print(f"Skipping {name}, already exists and valid.")
                return True
        except:
            pass
    
    print(f"Downloading {name} (ID: {instance_id})...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # content validation
        if b"<!DOCTYPE html>" in response.content[:100]:
             print(f"Error: Downloaded content for {name} seems to be an HTML page, not a VRP file.")
             return False
             
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Successfully downloaded {name}.vrp")
        return True
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        return False

def main():
    # 1. Get Mapping
    mapping = get_instance_mapping()
    
    if not mapping:
        print("Failed to get instance mapping.")
        return

    # 2. Select Instances to Download
    # User wanted Set A (A-n32-k5 to A-n80-k10)
    # We can also download Set P or B if desired.
    # Let's target Set A for now as requested.
    
    target_prefixes = ["A-n", "P-n", "B-n"]
    
    count = 0
    for name, instance_id in mapping.items():
        # Check if name matches our targets
        if any(name.startswith(prefix) for prefix in target_prefixes):
            success = download_instance(name, instance_id)
            if success:
                count += 1
                
    print(f"Finished. Downloaded {count} instances to {DATA_DIR}")

if __name__ == "__main__":
    main()
