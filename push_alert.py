import requests
import time
from datetime import datetime, timedelta, timezone

# === CONFIG ===
PUSHBULLET_TOKEN = <addtokenhere>
CHANNEL_TAG = <chanelname>

# Pakistan timezone
PKT = timezone(timedelta(hours=5))

# Define approximate solar window (adjust for your region/season if needed)
SOLAR_START = 6    # 6:00 AM
SOLAR_END = 18.5   # 6:30 PM (18.5 hours)

# API URLs
API_URL_1 = 'https://web.dessmonitor.com/public/?sign=179bd0f7ced97b873c1c3f937551eac4a1063e37&salt=1758621199735&token=CN826c1425-2a2e-4735-92af-c4c577715217&action=querySPDeviceLastData&source=1&devcode=6428&pn=W0051424410103&devaddr=1&sn=96142411101312&i18n=en_US'
API_URL_2 = 'https://web.dessmonitor.com/public/?sign=88cee9505e2fd9b5e999f2b926826e3e692bfe88&salt=1758621363179&token=CN826c1425-2a2e-4735-92af-c4c577715217&action=querySPDeviceLastData&source=1&devcode=2452&pn=W0036398935471&devaddr=1&sn=96142411100536&i18n=en_US'

ERROR_API_TEMPLATE = (
    "https://web.dessmonitor.com/public/?sign=10ce1e30c3baa71d3cef88b9a0ca721b5351cfc0"
    "&salt=1758211053384"
    "&token=b1793f103fbfc825c9939b86401a851ceb2ac28c20ad4fd67daffb63acfa2fcc"
    "&action=webQueryPlantsWarning&source=1"
    "&sn={SN}&pn={PN}&handle=true&devtype=2304&i18n=en_US&pagesize=15&page=0"
)

DEVICES = [
    {"name": "1st Floor", "sn": "96142411101312", "pn": "W0051424410103", "api": API_URL_1},
    {"name": "Ground Floor", "sn": "96142411100536", "pn": "W0036398935471", "api": API_URL_2},
]

last_error_ids = {}

# === HELPERS ===

def send_notification_to_channel(title, body):
    """Send Pushbullet notification to channel"""
    try:
        data = {"type": "note", "title": title, "body": body, "channel_tag": CHANNEL_TAG}
        r = requests.post("https://api.pushbullet.com/v2/pushes",
                          json=data,
                          headers={"Access-Token": PUSHBULLET_TOKEN},
                          timeout=10)
        print(f"📤 Channel notification sent: {r.status_code}")
    except Exception as e:
        print(f"⚠ Failed channel notification: {e}")

def send_notification_to_self(title, body):
    """Send Pushbullet notification to self (errors, logs)"""
    try:
        data = {"type": "note", "title": title, "body": body}
        r = requests.post("https://api.pushbullet.com/v2/pushes",
                          json=data,
                          headers={"Access-Token": PUSHBULLET_TOKEN},
                          timeout=10)
        print(f"📤 Self notification sent: {r.status_code}")
    except Exception as e:
        print(f"⚠ Failed self notification: {e}")

def find_value_by_id(obj, target_id):
    """Find inverter value by 'id' recursively"""
    if isinstance(obj, dict):
        if obj.get("id") == target_id:
            try:
                return float(obj.get("val", 0))
            except (TypeError, ValueError):
                return 0
        for v in obj.values():
            result = find_value_by_id(v, target_id)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_value_by_id(item, target_id)
            if result is not None:
                return result
    return None

def find_load_anywhere(obj):
    """Find load value (id or parameter match)"""
    if isinstance(obj, dict):
        if obj.get("id") == "bt_load_active_power_sole" or obj.get("par") == "AC output active power":
            try:
                return float(obj.get("val", 0))
            except (TypeError, ValueError):
                return 0
        for v in obj.values():
            result = find_load_anywhere(v)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_load_anywhere(item)
            if result is not None:
                return result
    return None

def get_inverter_data(api_url):
    """Fetch PV and Load from inverter API"""
    try:
        r = requests.get(api_url, timeout=20)
        if r.status_code != 200:
            msg = f"⚠ API error: HTTP {r.status_code}"
            print(msg)
            send_notification_to_self("⚠ API Error", msg)
            return (0, 0)

        data = r.json()
        pv1 = find_value_by_id(data, "bt_inputpower_1") or 0
        pv2 = find_value_by_id(data, "bt_inp_power_2") or 0
        load = find_load_anywhere(data) or 0
        return (pv1 + pv2, load)

    except Exception as e:
        msg = f"⚠ Exception fetching data: {e}"
        print(msg)
        send_notification_to_self("⚠ Exception Occurred", msg)
        return (0, 0)

def check_unhandled_errors(device):
    """Check and notify unhandled inverter errors"""
    global last_error_ids
    api_url = ERROR_API_TEMPLATE.format(SN=device["sn"], PN=device["pn"])
    try:
        r = requests.get(api_url, timeout=20)
        data = r.json()
        warnings = data.get("dat", {}).get("data", [])

        new_errors = []
        current_error_ids = set()

        for w in warnings:
            if not w.get("handled", True):
                error_id = w.get("id")
                error_msg = w.get("msg", "Unknown error")
                current_error_ids.add(error_id)

                if error_id not in last_error_ids.get(device["sn"], set()):
                    new_errors.append(error_msg)

        last_error_ids[device["sn"]] = current_error_ids

        if new_errors:
            msg = f"{device['name']} has new error(s):\n" + "\n".join(new_errors)
            print(f"⚠ {msg}")
            send_notification_to_self(f"⚠ {device['name']} Error", msg)
        elif not current_error_ids:
            print(f"ℹ No unhandled errors for {device['name']}")

    except Exception as e:
        print(f"⚠ Error checking errors for {device['name']}: {e}")

def is_solar_window(now):
    """Check if current time is within solar window"""
    hour = now.hour + now.minute/60.0
    return SOLAR_START <= hour <= SOLAR_END

# === MAIN LOOP ===

if __name__ == "__main__":
    while True:
        now_local = datetime.now(timezone.utc).astimezone(PKT)
        print(f"\n🕒 Current Pakistan time: {now_local.strftime('%Y-%m-%d %H:%M:%S')}")

        for device in DEVICES:
            pv_total, load = get_inverter_data(device["api"])
            print(f"{device['name']} → PV: {pv_total}W | Load: {load}W")

            # Only check solar vs load inside solar window
            if is_solar_window(now_local):
                if load > pv_total:
                    msg = f"{device['name']}:\nSolar: {pv_total}W\nLoad: {load}W\n\n⚡ Reduce your Load!"
                    send_notification_to_channel(f"⚡ {device['name']} Solar Alert", msg)
                else:
                    print(f"ℹ {device['name']}: No alert, PV covers load.")
            else:
                print(f"🌙 {device['name']}: Outside solar window, skipping PV alert.")

            # Error checks always (day & night)
            check_unhandled_errors(device)

        # Sleep 5 minutes before next check
        time.sleep(300)

