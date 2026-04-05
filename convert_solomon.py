import json
import os
import glob

def convert_solomon_to_go(input_file, output_file, max_customers=15):
    with open(input_file, 'r') as f:
        data = json.load(f)

    depot = data['customers'][0]
    
    batch = {
        "timeReady": 0,
        "ori": [],
        "des": []
    }
    
    # Only take first max_customers customers (excluding depot)
    customers = data['customers'][1:max_customers+1]
    
    for cust in customers:
        # Origin (Depot)
        ori_station = {
            "x": int(depot['x']),
            "y": int(depot['y']),
            "timeStart": int(depot['earliest']),
            "timeEnd": int(depot['latest']),
            "reqCode": 0,
            "load": 0
        }
        # Destination (Customer)
        des_station = {
            "x": int(cust['x']),
            "y": int(cust['y']),
            "timeStart": int(cust['earliest']),
            "timeEnd": int(cust['latest']),
            "reqCode": 0,
            "load": int(cust['demand'])
        }
        batch["ori"].append(ori_station)
        batch["des"].append(des_station)
    
    go_input = {
        "loadCap": int(data['capacity']),
        "vehicleNum": int(data['vehicle-nr']),
        "batch": [batch]
    }
    
    with open(output_file, 'w') as f:
        json.dump(go_input, f, indent=4)

# Use absolute paths
root_dir = r'c:\Users\24294\.trae\Agent_EOH'
output_dir = os.path.join(root_dir, 'Archive_extracted', 'solomon_benchmark')
benchmark_dir = os.path.join(root_dir, 'solomon_benchmarks', 'solomon-vrptw-benchmarks-main', 'rc', '1')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Find all rc1*.json files
pattern = os.path.join(benchmark_dir, 'rc1*.json')
print(f"Searching for files with pattern: {pattern}")
for input_file in glob.glob(pattern):
    filename = os.path.basename(input_file)
    output_file = os.path.join(output_dir, filename)
    print(f"Converting {input_file} to {output_file} (limited to 15 customers)...")
    convert_solomon_to_go(input_file, output_file, max_customers=15)

print("Conversion complete.")
