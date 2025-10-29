"""
Test script to verify error rate alert calculation logic
"""
import pandas as pd

# Simulate the test_sample_data.csv
data = {
    'ID': ['001', '002', '001', '003', '004', '005', '002', '006', '007', '008'],
    'Name': ['John Smith', 'Jane Doe', 'John Williams', 'Bob Johnson', 'Alice Brown', 
             'Charlie Davis', 'Jane Smith', 'David Wilson', 'Emma Taylor', 'Frank Miller'],
    'Email': ['john@email.com', 'jane@email.com', None, 'bob@email.com', 'alice@email.com',
              None, 'janes@email.com', 'david@email.com', 'emma@email.com', None],
    'Department': ['IT', 'HR', 'Marketing', 'IT', 'Finance', 'IT', 'Finance', 'HR', 'Marketing', 'IT'],
    'Salary': [50000, 45000, 55000, 50000, 48000, 52000, 48000, 46000, 49000, 51000],
    'JoinDate': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19',
                 '2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24']
}

df = pd.DataFrame(data)

print("="*60)
print("TESTING ERROR RATE ALERT LOGIC")
print("="*60)
print(f"\nTotal rows in CSV: {len(df)}")

# Simulate duplicate detection based on ID column
duplicate_id_column = "ID"
if duplicate_id_column in df.columns:
    dup_mask = df.duplicated(subset=[duplicate_id_column], keep=False)
else:
    dup_mask = df.duplicated(keep=False)

print(f"\nDuplicate rows detected: {dup_mask.sum()}")
print(f"Duplicate IDs: {df[dup_mask]['ID'].unique().tolist()}")

# Simulate missing detection (warnings)
quality_cols = ['Email']  # Example: checking Email for missing values
missing_mask = df[quality_cols].isna().any(axis=1)
warning_mask = missing_mask & (~dup_mask)
error_mask = dup_mask
valid_mask = ~(warning_mask | error_mask)

print(f"\nMissing values (warnings only): {warning_mask.sum()}")
print(f"Errors (duplicates): {error_mask.sum()}")
print(f"Valid rows: {valid_mask.sum()}")

# Simulate aggregation (single snapshot - no date grouping)
valid_count = int(valid_mask.sum())
warning_count = int(warning_mask.sum())
error_count = int(error_mask.sum())

print(f"\n--- Aggregated Counts ---")
print(f"Valid: {valid_count}")
print(f"Warning: {warning_count}")
print(f"Error: {error_count}")

# Simulate the alert calculation
_latest_valid = float(valid_count)
_latest_warn = float(warning_count)
_latest_err = float(error_count)
latest_total = max(1, int(round(_latest_valid + _latest_warn + _latest_err)))
latest_error_rate = min(100.0, 100.0 * (_latest_err / latest_total))

print(f"\n--- Error Rate Calculation ---")
print(f"Latest total: {latest_total}")
print(f"Latest error count: {_latest_err}")
print(f"Latest error rate (percentage): {latest_error_rate:.1f}%")

# Convert to 1-20 scale
latest_error_on_scale = latest_error_rate / 5
print(f"Latest error rate (1-20 scale): {latest_error_on_scale:.1f}/20")

# Test different thresholds
print(f"\n--- Testing Different Thresholds ---")
for threshold in [1, 5, 8, 10, 15, 20]:
    threshold_pct = threshold * 5
    will_alert = latest_error_rate > threshold_pct
    print(f"Threshold: {threshold}/20 ({threshold_pct}%) -> Alert: {'YES ⚠️' if will_alert else 'NO'}")

print(f"\n{'='*60}")
print(f"CONCLUSION:")
print(f"{'='*60}")
print(f"With {error_count} errors out of {latest_total} total records:")
print(f"  - Error rate is {latest_error_on_scale:.1f}/20 ({latest_error_rate:.1f}%)")
print(f"  - Alert will show if threshold < {int(latest_error_on_scale)}")
print(f"  - Default threshold is 10/20 (50%)")
print(f"  - Alert will {'SHOW' if latest_error_rate > 50 else 'NOT SHOW'} with default threshold")
print(f"{'='*60}\n")
