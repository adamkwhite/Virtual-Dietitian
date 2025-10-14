#!/usr/bin/env python3
"""Direct test of USDA API to diagnose issues."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('USDA_API_KEY')
print(f'API Key: {api_key[:10]}... (length: {len(api_key)})')
print()

# Test 1: Simple search
print("Test 1: Search for 'apple'")
url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
params = {'api_key': api_key, 'query': 'apple', 'pageSize': 1}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'✓ Success! Found {data.get("totalHits", 0)} results')
        if data.get('foods'):
            food = data['foods'][0]
            print(f'  First result: {food.get("description")}')
    else:
        print(f'✗ Error: {response.text[:200]}')
except Exception as e:
    print(f'✗ Exception: {e}')

print()

# Test 2: Search for 'pizza'
print("Test 2: Search for 'pizza'")
params = {'api_key': api_key, 'query': 'pizza', 'pageSize': 1}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'✓ Success! Found {data.get("totalHits", 0)} results')
        if data.get('foods'):
            food = data['foods'][0]
            print(f'  First result: {food.get("description")}')
    else:
        print(f'✗ Error: {response.text}')
except Exception as e:
    print(f'✗ Exception: {e}')

print()

# Test 3: Search for 'sushi'
print("Test 3: Search for 'sushi'")
params = {'api_key': api_key, 'query': 'sushi', 'pageSize': 1}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f'Status: {response.status_code}')

    if response.status_code == 200:
        data = response.json()
        print(f'✓ Success! Found {data.get("totalHits", 0)} results')
        if data.get('foods'):
            food = data['foods'][0]
            print(f'  First result: {food.get("description")}')
    else:
        print(f'✗ Error: {response.text[:200]}')
except Exception as e:
    print(f'✗ Exception: {e}')
