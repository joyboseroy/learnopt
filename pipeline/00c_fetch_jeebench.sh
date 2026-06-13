#!/bin/bash
mkdir -p ~/learnopt/data/jee
cd ~/learnopt/data/jee

# Clone the repo (small) to get dataset.zip
git clone --depth 1 https://github.com/dair-iitd/jeebench.git
cd jeebench

# Find and unzip the dataset
find . -iname "*.zip"
unzip -o data/dataset.zip -d ../jeebench_data 2>/dev/null || \
unzip -o dataset.zip -d ../jeebench_data 2>/dev/null || \
find . -iname "dataset.zip" -exec unzip -o {} -d ../jeebench_data \;

cd ..
ls -la jeebench_data/

python3 << 'EOF'
import json
import glob

files = glob.glob("jeebench_data/**/*.json", recursive=True) + glob.glob("jeebench_data/*.json")
print("JSON files found:", files)

for f in files:
    try:
        data = json.load(open(f))
        print(f"\n{f}: {len(data) if isinstance(data, list) else 'dict'} items")
        if isinstance(data, list) and len(data) > 0:
            print("Sample keys:", list(data[0].keys()))
            print("Sample item:", json.dumps(data[0], indent=2)[:500])
            # check for year field
            if 'year' in data[0] or any('year' in str(k).lower() for k in data[0].keys()):
                years = [d.get('year') for d in data if 'year' in d]
                print("Year distribution sample:", years[:20])
    except Exception as e:
        print(f"{f}: failed to parse -- {e}")
EOF
