
import pandas as pd

df = pd.read_csv("network_features.csv")

df["total_packets"] = (
    df["packets_sent"] + df["packets_received"]
)

df["total_bytes"] = (
    df["bytes_sent"] + df["bytes_received"]
)

print("\nTOP 10 FLOWS BY DATA VOLUME")
print("============================")

print(
    df.nlargest(10, "total_bytes")[
        [
            "source_ip",
            "destination_ip",
            "destination_port",
            "protocol",
            "total_packets",
            "total_bytes",
            "duration",
            "alerted"
        ]
    ].to_string(index=False)
)

print("\nTOP 10 FLOWS BY PACKET COUNT")
print("============================")

print(
    df.nlargest(10, "total_packets")[
        [
            "source_ip",
            "destination_ip",
            "destination_port",
            "protocol",
            "total_packets",
            "total_bytes",
            "duration"
        ]
    ].to_string(index=False)
)
