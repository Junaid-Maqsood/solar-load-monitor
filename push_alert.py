import requests

# === CONFIG ===
PUSHBULLET_TOKEN = 'o.snUuOZLqTvUQ0EDJPZu1DePxzSJwhKNB'
CHANNEL_TAG = 'solaralert'

API_URL_1 = 'https://web.dessmonitor.com/public/?sign=43d88effb8c479157202abf439574e36d062a79a&salt=1751992371034&token=b1793f103fbfc825c9939b86401a851ceb2ac28c20ad4fd67daffb63acfa2fcc&action=querySPDeviceLastData&source=1&devcode=2452&pn=W0051424410103&devaddr=1&sn=96142411101312&i18n=en_US'

API_URL_2 = 'https://web.dessmonitor.com/public/?sign=9d73c40c042348ed931c65554d9a0a8d85a8c4c2&salt=1752041384124&token=b1793f103fbfc825c9939b86401a851ceb2ac28c20ad4fd67daffb63acfa2fcc&action=querySPDeviceLastData&source=1&devcode=2452&pn=W0036398935471&devaddr=1&sn=96142411100536&i18n=en_US'

# === FUNCTIONS ===

def send_notification_to_channel(title, body):
    data = {
        "type": "note",
        "title": title,
        "body": body,
        "channel_tag": CHANNEL_TAG
    }
    response = requests.post(
        'https://api.pushbullet.com/v2/pushes',
        json=data,
        headers={'Access-Token': PUSHBULLET_TOKEN}
    )
    print(f"Notification to channel status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Notification sent to channel!")
    else:
        print("⚠ Error sending to channel:", response.text)

def send_notification_to_self(title, body):
    data = {
        "type": "note",
        "title": title,
        "body": body
    }
    response = requests.post(
        'https://api.pushbullet.com/v2/pushes',
        json=data,
        headers={'Access-Token': PUSHBULLET_TOKEN}
    )
    print(f"Notification to self status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Private notification sent to you!")
    else:
        print("⚠ Error sending private notification:", response.text)

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
            return (0, 0, 0)

        data = response.json()
        pv1 = find_value_by_id(data, "bt_inputpower_1") or 0
        pv2 = find_value_by_id(data, "bt_inp_power_2") or 0
        load = find_load_anywhere(data) or 0
        return (pv1, pv2, load)

    except requests.exceptions.Timeout:
        msg = "⚠ Timeout: API server took too long to respond."
        print(msg)
        send_notification_to_self("⚠ Timeout", msg)
        return (0, 0, 0)

    except Exception as e:
        msg = f"⚠ Exception: {e}"
        print(msg)
        send_notification_to_self("⚠ Exception Occurred", msg)
        return (0, 0, 0)

# === MAIN FUNCTION ===

def main():
    # Check 1st Floor
    pv1_1, pv2_1, load_1 = get_inverter_data(API_URL_1)
    pv_total_1 = pv1_1 + pv2_1
    print(f"1st Floor → PV Total: {pv_total_1}W | Load: {load_1}W")

    if pv_total_1 > 50 and load_1 > pv_total_1:
        message = f"1st Floor:\nSolar: {pv_total_1}W\nLoad: {load_1}W\n\nReduce your Load!"
        send_notification_to_channel("⚡ 1st Floor Solar Update", message)
    else:
        print("ℹ 1st Floor: No alert needed.")

    # Check Ground Floor
    pv1_2, pv2_2, load_2 = get_inverter_data(API_URL_2)
    pv_total_2 = pv1_2 + pv2_2
    print(f"Ground Floor → PV Total: {pv_total_2}W | Load: {load_2}W")

    if pv_total_2 > 50 and load_2 > pv_total_2:
        message = f"Ground Floor:\nSolar: {pv_total_2}W\nLoad: {load_2}W\n\nReduce your Load!"
        send_notification_to_channel("⚡ Ground Floor Solar Update", message)
    else:
        print("ℹ Ground Floor: No alert needed.")

if __name__ == "__main__":
    main()
