# %% Imports and Config
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

CACHE_DIR = "cache/invoices_00"

# %% Load Data
file_path = os.path.join(CACHE_DIR, "all.json")

try:
    with open(file_path, "r", encoding="utf-8") as f:
        invoices = json.load(f)
    print(f"Loaded {len(invoices)} invoices from {file_path}")
except FileNotFoundError:
    print(f"File not found: {file_path}")
    invoices = []

# %% Process Data
# Group invoices by their month (YYYY-MM) derived from invoiceDate
monthly_invoices = defaultdict(list)

for invoice in invoices:
    date_str = invoice.get("invoiceDate")
    amount = invoice.get("amount", 0.0)
    inv_num = invoice.get("invoiceNumber", "Unknown")
    
    if date_str and amount > 0:
        # Extract the 'YYYY-MM' prefix from 'YYYY-MM-DD'
        month_key = date_str[:7]
        monthly_invoices[month_key].append({"amount": amount, "invoiceNumber": inv_num})

# Create a continuous range of months to avoid skipping missing months
sorted_months = sorted(monthly_invoices.keys())
if sorted_months:
    start_dt = datetime.strptime(sorted_months[0], "%Y-%m")
    end_dt = datetime.strptime(sorted_months[-1], "%Y-%m")
    
    all_months = []
    curr = start_dt
    while curr <= end_dt:
        all_months.append(curr.strftime("%Y-%m"))
        y, m = curr.year, curr.month
        if m == 12:
            m = 1
            y += 1
        else:
            m += 1
        curr = datetime(y, m, 1)
    
    sorted_months = all_months

print(f"Data spans {len(sorted_months)} months continuously.")

# %% Plot Data
fig, ax = plt.subplots(figsize=(14, 8))

colors = [
    "#4A90E2", "#50E3C2", "#F5A623", "#E24A4A", 
    "#B8E986", "#BD10E0", "#9013FE", "#8B572A", 
    "#F8E71C", "#7ED321", "#417505", "#4A4A4A"
]

for x_pos, month in enumerate(sorted_months):
    # Ensure the month appears on the x-axis even if there are no invoices
    ax.bar(month, 0)
    
    items = monthly_invoices.get(month, [])
    # Sort by amount descending, so the largest chunks are at the bottom
    items.sort(key=lambda x: x["amount"], reverse=True)
    
    current_bottom = 0.0
    for i, item in enumerate(items):
        amount = item["amount"]
        inv_num = item["invoiceNumber"]
        
        # Plot stacked bar segment
        color = colors[i % len(colors)]
        ax.bar(month, amount, bottom=current_bottom, color=color, edgecolor="white", width=0.7)
        
        # Place label in the middle of the segment if it's comfortably large
        if amount > 15:
            # We add a subtle white background box to the text to ensure it's readable over any color
            ax.text(x_pos, current_bottom + amount / 2, f"#{inv_num}\n{amount:.2f}", 
                    ha='center', va='center', rotation=0, fontsize=9, color="black", 
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.75, edgecolor="none"))
                    
        current_bottom += amount

plt.title("Total Invoiced Amount per Month (Segmented by Invoice)", fontsize=16)
plt.xlabel("Month (YYYY-MM)", fontsize=12)
plt.ylabel("Amount (CHF)", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()

# Save out the plot to cache dir simply as a side-effect, then show it
save_path = os.path.join(CACHE_DIR, "monthly_totals.png")
if invoices:
    plt.savefig(save_path, dpi=300)
    print(f"✅ Plot saved to {save_path}")

plt.show()

