import requests
import time
from datetime import datetime, timezone, timedelta

# === CONFIG ===
PUSHBULLET_TOKEN = 'o.snUuOZLqTvUQ0EDJPZu1DePxzSJwhKNB'
CHANNEL_TAG = 'solaralert'

API_URL_1 = 'https://web.dessmonitor.com/public/?sign=43d88effb8c479157202abf439574e36d062a79a&salt=1751992371034&token=b1793f103fbfc825c9939b86401a851ceb2ac28c20ad4fd67daffb63acfa2fcc&action=querySPDeviceLastData&source=1&devcode=2452&pn=W0051424410103&devaddr=1&sn=96142411101312&i18n=en_US'

API_URL_2 = 'https://web.dessmonitor.com/public/?sign=9d73c40c042348ed931c65554d9a0a8d85a8c4c2&salt=1752041384124&token=b1793f103fbfc825c9939b86401a851ceb2ac28c20ad4fd67daffb63acfa2fcc&action=querySPDeviceLastData&source=1&devcode=2452&pn=W0036398935471&devaddr=1&sn=96142411100536&i18n=en_US'

# === FUNCTIONS ===

def send_notification_to_channel(title, body):
    data = {"type": "note", "title": title, "body": body, "channel_tag": CHANNEL_TAG}
    response = requests.post('https://api.pushbullet.com/v2/pushes', json=data,
                             headers={'Access-Token': PUSHBULLET_TOKEN})
    print(f"Notification to channel status: {response.status_code}")

def send_notification_to_self(title, body):
    data = {"type": "note", "title": title, "body": body}
    response = requests.post('https://api.pushbullet.com/v2/pushes', json=data,
                             headers={'Access-Token': PUSHBULLET_TOKEN})
    print(f"Notification to self status: {response.status_code}")

def find_value_by_id(obj, target_id):
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
    try:
        response = requests.get(api_url, timeout=20)
        if response.status_code != 200:
            msg = f"⚠ API error: HTTP {response.status_code}"
            print(msg)
            send_notification_to_self("⚠ API Error", msg)
            return (0, 0, 0, None)

        data = response.json()
        timestamp_str = data.get("dat", {}).get("gts", None)

        pv1 = find_value_by_id(data, "bt_inputpower_1") or 0
        pv2 = find_value_by_id(data, "bt_inp_power_2") or 0
        load = find_load_anywhere(data) or 0

        return (pv1, pv2, load, timestamp_str)

    except requests.exceptions.Timeout:
        msg = "⚠ Timeout: API server took too long to respond."
        print(msg)
        send_notification_to_self("⚠ Timeout", msg)
        return (0, 0, 0, None)

    except Exception as e:
        msg = f"⚠ Exception: {e}"
        print(msg)
        send_notification_to_self("⚠ Exception Occurred", msg)
        return (0, 0, 0, None)

# === MAIN LOOP ===
if __name__ == "__main__":
    while True:
        now_utc = datetime.now(timezone.utc)
        now_pak = now_utc + timedelta(hours=5)
        hour = now_pak.hour
        minute = now_pak.minute
        print(f"\n🕒 Current Pakistan time: {hour}:{minute:02d}")

        if 4 <= hour < 19:  # between 4 AM and 7 PM
            # Check 1st Floor
            pv1_1, pv2_1, load_1, ts_1 = get_inverter_data(API_URL_1)
            pv_total_1 = pv1_1 + pv2_1
            print(f"1st Floor → PV Total: {pv_total_1}W | Load: {load_1}W | Timestamp: {ts_1}")

            if ts_1:
                try:
                    ts_time = datetime.strptime(ts_1, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) + timedelta(hours=5)
                    age = (now_pak - ts_time).total_seconds() / 60
                    if age > 30:
                        print(f"⚠ Stale data detected: data is {int(age)} minutes old (timestamp: {ts_1})")
                        send_notification_to_self("⚠ Stale Data on 1st Floor", f"Data is {int(age)} minutes old! Timestamp: {ts_1}")
                except Exception as e:
                    print(f"⚠ Error parsing timestamp: {e}")

            if pv_total_1 > 350 and load_1 > pv_total_1:
                message = f"1st Floor:\nSolar: {pv_total_1}W\nLoad: {load_1}W\n\nReduce your Load!"
                send_notification_to_channel("⚡ 1st Floor Solar Update", message)
            else:
                print("ℹ 1st Floor: No alert needed.")

            # Check Ground Floor
            pv1_2, pv2_2, load_2, ts_2 = get_inverter_data(API_URL_2)
            pv_total_2 = pv1_2 + pv2_2
            print(f"Ground Floor → PV Total: {pv_total_2}W | Load: {load_2}W | Timestamp: {ts_2}")

            if ts_2:
                try:
                    ts_time = datetime.strptime(ts_2, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) + timedelta(hours=5)
                    age = (now_pak - ts_time).total_seconds() / 60
                    if age > 30:
                        print(f"⚠ Stale data detected: data is {int(age)} minutes old (timestamp: {ts_2})")
                        send_notification_to_self("⚠ Stale Data on Ground Floor", f"Data is {int(age)} minutes old! Timestamp: {ts_2}")
                except Exception as e:
                    print(f"⚠ Error parsing timestamp: {e}")

            if pv_total_2 > 350 and load_2 > pv_total_2:
                message = f"Ground Floor:\nSolar: {pv_total_2}W\nLoad: {load_2}W\n\nReduce your Load!"
                send_notification_to_channel("⚡ Ground Floor Solar Update", message)
            else:
                print("ℹ Ground Floor: No alert needed.")

        else:
            print("🌙 Outside selected hours, skipping check.")

        time.sleep(300)  # wait 5 minutes before next check
