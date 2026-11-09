import pandas as pd

df = pd.read_csv("network_features.csv")

df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

profile = (
    df.groupby(["protocol", "destination_port"])
    .agg(
        flow_count=("protocol", "size"),
        avg_packets=("total_packets", "mean"),
        max_packets=("total_packets", "max"),
        avg_bytes=("total_bytes", "mean"),
        max_bytes=("total_bytes", "max")
    )
    .reset_index()
    .sort_values("flow_count", ascending=False)
)

print("\nSERVICE-WISE TRAFFIC PROFILE")
print("============================")
print(profile.to_string(index=False))

profile.to_csv("service_profile.csv", index=False)

print("\nSaved: service_profile.csv")
