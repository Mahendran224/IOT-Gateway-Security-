
import json
import pandas as pd

# Known devices and expected dashboard service
LAPTOP_IP = "10.141.120.74"
PI_IP = "10.141.120.2"
DASHBOARD_PORT = 5000

INPUT_FILE = "network_anomaly_results_v4.csv"
OUTPUT_FILE = "network_context_results.csv"
EVE_FILE = "/var/log/suricata/eve.json"


def load_suricata_events():
    events = {}

    with open(EVE_FILE, "r", encoding="utf-8",
              errors="replace") as file:
        for line in file:
            try:
                data = json.loads(line)
                flow_id = data.get("flow_id")

                if flow_id is not None:
                    events.setdefault(flow_id, []).append(data)

            except json.JSONDecodeError:
                continue

    return events


def validate_context(row, events):
    flow_id = row["flow_id"]
    records = events.get(flow_id, [])

    known_pair = (
        (row["src_ip"] == LAPTOP_IP and row["dest_ip"] == PI_IP)
        or
        (row["src_ip"] == PI_IP and row["dest_ip"] == LAPTOP_IP)
    )

    http_records = [
        event for event in records
        if event.get("event_type") == "http"
    ]

    alert_records = [
        event for event in records
        if event.get("event_type") == "alert"
    ]

    dashboard_verified = False

    for event in http_records:
        http = event.get("http", {})

        if (
            event.get("dest_port") == DASHBOARD_PORT
            and http.get("http_method") == "GET"
            and http.get("status") == 200
            and known_pair
        ):
            dashboard_verified = True
            break

    if dashboard_verified:
        context = "KNOWN_DASHBOARD_COMMUNICATION"
    elif known_pair:
        context = "KNOWN_DEVICE_PAIR_PROTOCOL_UNCONFIRMED"
    else:
        context = "UNRECOGNIZED_DEVICE_PAIR"

    signatures = sorted({
        event.get("alert", {}).get("signature", "Unknown")
        for event in alert_records
    })

    return pd.Series({
        "device_pair_known": known_pair,
        "dashboard_verified": dashboard_verified,
        "context_assessment": context,
        "suricata_alert_count": len(alert_records),
        "suricata_signatures": "; ".join(signatures)
    })


def main():
    print("Loading V4 anomaly results...")
    df = pd.read_csv(INPUT_FILE)

    print("Reading Suricata events...")
    events = load_suricata_events()

    print("Validating network context...")
    context = df.apply(
        lambda row: validate_context(row, events),
        axis=1
    )

    result = pd.concat([df, context], axis=1)

    result.to_csv(OUTPUT_FILE, index=False)

    print("\nCONTEXT VALIDATION COMPLETED")
    print("Total flows:", len(result))
    print("\nContext assessment:")
    print(result["context_assessment"].value_counts().to_string())

    print("\nSuricata alert counts:")
    print(result["suricata_alert_count"].value_counts().to_string())

    print("\nOutput saved to:", OUTPUT_FILE)
    print("Original V4 results remain unchanged.")


if __name__ == "__main__":
    main()


