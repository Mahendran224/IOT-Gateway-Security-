import pandas as pd

df = pd.read_csv("network_flow_ml.csv")

tcp = df[df["protocol"] == "TCP"].copy()

print("\nTCP METADATA QUALITY")
print("Total TCP flows:", len(tcp))

for column in [
    "tcp_syn",
    "tcp_ack",
    "tcp_fin",
    "tcp_rst"
]:
    print(f"\n{column}")
    print(tcp[column].value_counts(dropna=False))

print("\nTCP FLAGS MISSING BY CONNECTION STATE")

for column in [
    "tcp_syn",
    "tcp_ack",
    "tcp_fin",
    "tcp_rst"
]:
    print(f"\n{column}")
    print(
        tcp.groupby("connection_state", dropna=False)[column]
        .apply(lambda x: x.isna().sum())
    )

print("\nTCP APPLICATION PROTOCOL")
print(tcp["app_protocol"].value_counts(dropna=False))

print("\nTCP CONNECTION STATE")
print(tcp["connection_state"].value_counts(dropna=False))

print("\nTCP FLAG COMPLETENESS")
print(
    tcp[["tcp_syn", "tcp_ack", "tcp_fin", "tcp_rst"]]
    .notna()
    .sum()
)
