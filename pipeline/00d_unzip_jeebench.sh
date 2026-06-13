#!/bin/bash
cd ~/learnopt/data/jee/jeebench

unzip -o data.zip -d ../jeebench_data
cd ..
echo "=== Extracted structure ==="
find jeebench_data -type f | head -30

python3 << 'EOF'
import json
import glob

files = glob.glob("jeebench_data/**/*.json", recursive=True)
print("\nJSON files found:", files)

for f in files:
    try:
        data = json.load(open(f))
        if isinstance(data, list):
            print(f"\n{f}: {len(data)} items")
            if len(data) > 0:
                print("Sample keys:", list(data[0].keys()))
                print("Sample item:")
                print(json.dumps(data[0], indent=2)[:800])
                # year distribution
                keys = data[0].keys()
                year_key = [k for k in keys if 'year' in k.lower() or 'desc' in k.lower()]
                print("Possible year-related keys:", year_key)
                if year_key:
                    from collections import Counter
                    print(Counter([d.get(year_key[0]) for d in data]))
        else:
            print(f"\n{f}: dict with keys {list(data.keys())[:10]}")
    except Exception as e:
        print(f"{f}: failed -- {e}")
EOF
