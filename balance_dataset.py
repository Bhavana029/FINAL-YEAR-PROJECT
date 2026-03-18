import pandas as pd
from sklearn.utils import resample
import os

# ===============================
# PATH
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "BloodEye_Realtime_Synthetic_Dataset_3000_Rows.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "BloodEye_Balanced_2400_Rows.csv"
)

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(DATASET_PATH)

print("Original distribution:")
print(df["blood_group"].value_counts())

# ===============================
# BALANCE DATA
# ===============================
TARGET_COUNT = 300   # per blood group

balanced_groups = []

for blood_group, group_df in df.groupby("blood_group"):
    if len(group_df) > TARGET_COUNT:
        # Downsample
        balanced = group_df.sample(TARGET_COUNT, random_state=42)
    else:
        # Upsample
        balanced = resample(
            group_df,
            replace=True,
            n_samples=TARGET_COUNT,
            random_state=42
        )
    balanced_groups.append(balanced)

# ===============================
# COMBINE & SHUFFLE
# ===============================
balanced_df = pd.concat(balanced_groups)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

# ===============================
# SAVE
# ===============================
balanced_df.to_csv(OUTPUT_PATH, index=False)

print("\nBalanced distribution:")
print(balanced_df["blood_group"].value_counts())

print("\n✅ Balanced dataset created successfully!")
print(f"Saved at: {OUTPUT_PATH}")
