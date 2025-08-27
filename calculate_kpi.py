import pandas as pd
import datetime
import json

file_path = r'C:\Users\DELL\Documents\Internship Task\shipzu_sample_orders_IST.csv'
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found. Please ensure it's in the same directory.")
    exit()

# current time in IST
now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

# Converting created at as a datetime object
df['created_at'] = pd.to_datetime(df['created_at'])

# KPI 1: Delivered % 
delivered_count = len(df[df['current_status'] == 'DELIVERED'])
cancelled_count = len(df[df['current_status'] == 'CANCELLED'])
denominator_delivered = len(df) - cancelled_count
delivered_percent = (delivered_count / denominator_delivered) * 100 if denominator_delivered != 0 else 0.0

# KPI 2: RTO %
rto_delivered_count = len(df[df['current_status'] == 'RTO_DELIVERED'])
denominator_rto = delivered_count + rto_delivered_count
rto_percent = (rto_delivered_count / denominator_rto) * 100 if denominator_rto != 0 else 0.0

# KPI 3: Orders at Risk 
orders_at_risk_count = len(df[
    ((df['current_status'] == 'OUT_FOR_DELIVERY') & (df['days_in_state'] > 2)) |
    ((df['current_status'] == 'IN_TRANSIT') & (df['days_in_state'] > 5)) |
    ((df['current_status'] == 'NDR') & (df['ndr_open'] == True) & (df['days_in_state'] > 1))
])

# KPI 4: DRR (Daily Run Rate)
last_7_days = now_ist - datetime.timedelta(days=7)
delivered_in_last_7_days = len(df[
    (df['current_status'] == 'DELIVERED') &
    (df['created_at'] >= last_7_days)
])
drr = delivered_in_last_7_days / 7.0

# Creating submission.json 
submission_data = {
    "submitted_at_ist": now_ist.isoformat(),
    "kpi": {
        "delivered_percent": round(delivered_percent, 2),
        "rto_percent": round(rto_percent, 2),
        "orders_at_risk": orders_at_risk_count,
        "drr": round(drr, 3)
    },
    "rules_thresholds": {
        "delivered_percent": 85,
        "rto_percent": 8,
        "orders_at_risk": 20
    },
    "rules_triggers": []
}

with open('submission.json', 'w') as f:
    json.dump(submission_data, f, indent=4)

print("\n--- Calculated KPIs ---")
print(f"Delivered %: {round(delivered_percent, 2)}")
print(f"RTO %: {round(rto_percent, 2)}")
print(f"Orders at Risk: {orders_at_risk_count}")
print(f"DRR: {round(drr, 3)}")
print("\nSuccessfully created 'submission.json'.")