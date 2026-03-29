# %% Setup
import requests
import os
import time
from config import COOKIE

BASE_URL = "https://www.kpt.ch/kpt-api/portal/protected/invoices"

headers = {
    "accept": "application/json",
    "cookie": COOKIE,
}

session = requests.Session()
session.headers.update(headers)


# %% Create incremental cache dir

import glob
import re

def create_incremental_cache_dir(cache_root="cache"):
    # Scans the cache root for existing 'invoices_XX' folders and creates the next sequential folder
    os.makedirs(cache_root, exist_ok=True)
    
    existing = glob.glob(os.path.join(cache_root, "invoices_*"))
    highest = -1
    for folder in existing:
        match = re.search(r"invoices_(\d+)$", folder)
        if match:
            highest = max(highest, int(match.group(1)))
            
    incremental_run_id = f"{highest + 1:02d}"
    cache_dir = os.path.join(cache_root, f"invoices_{incremental_run_id}")
    os.makedirs(cache_dir, exist_ok=True)
    
    return cache_dir

cache_dir = create_incremental_cache_dir("cache")

# %% Get all invoices

import json

page_size = 100
current_page = 1
total_pages = 1
all_invoices = []

while current_page <= total_pages:
    url = f"{BASE_URL}?pageNumber={current_page}&pageSize={page_size}&invoiceDateFrom=2022-01-01"
    
    try:
        res = session.get(url)

        if res.status_code == 200:
            resp_json = res.json()
            
            # Extract data and meta
            data = resp_json.get("data", [])
            meta = resp_json.get("meta", {}).get("page", {})
            
            all_invoices.extend(data)
            
            # Handle pagination
            total_pages = meta.get("totalPage", 1)
            print(f"✅ Fetched page {current_page}/{total_pages} (got {len(data)} invoices)")
            
            current_page += 1

        else:
            print(f"❌ Failed page {current_page}: {res.status_code}")
            print(res.text[:200])
            break

        time.sleep(0.3)  # be polite / avoid rate limits

    except Exception as e:
        print(f"💥 Error all: {e}")
        break

# Save all merged invoices to cache/invoices_<id>/all.json
file_path = os.path.join(cache_dir, "all.json")
with open(file_path, "w") as f:
    json.dump(all_invoices, f, indent=2)

print(f"✅ Saved {len(all_invoices)} merged invoices to {file_path}")

# %% Download PDFs

print(f"Downloading {len(all_invoices)} PDFs...")
pdf_base_url = "https://www.kpt.ch/kpt-api/portal/protected/documents/pdf"

for invoice in all_invoices:
    invoice_number = invoice.get("invoiceNumber")
    if not invoice_number:
        continue
        
    url = f"{pdf_base_url}/{invoice_number}?referenceType=InvoiceNumber"
    
    try:
        # Override the application/json accept header just for this request
        res = session.get(url, headers={"accept": "application/pdf"})
        if res.status_code == 200:
            pdf_path = os.path.join(cache_dir, f"{invoice_number}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(res.content)
            print(f"✅ Saved PDF {invoice_number}")
        else:
            print(f"❌ Failed PDF {invoice_number}: {res.status_code}")
            
        time.sleep(0.3)  # Be polite
    except Exception as e:
        print(f"💥 Error downloading PDF {invoice_number}: {e}")