import os
import time
import subprocess
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
HOST = os.getenv("HOST_TO_CHECK", "8.8.8.8")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))

def send_message(message: str) -> None:
    """
    Send a message via the Telegram Bot API.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        raise ValueError("TELEGRAM_TOKEN and CHAT_ID must be set as environment variables")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send message: {e}")

def is_host_reachable() -> bool:
    """
    Check if the host is reachable using the system ping command.
    Returns True if the host responds, otherwise False.
    """
    param = "-n" if os.name == "nt" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "1", HOST],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False

def main() -> None:
    """
    Main loop that checks host availability and sends Telegram notifications on status changes.
    """
    previous_status = None
    while True:
        current_status = is_host_reachable()
        if previous_status is None:
            # On first run, just record status without sending a message
            previous_status = current_status
        elif current_status != previous_status:
            status_str = "UP" if current_status else "DOWN"
            message = f"{HOST} is {status_str}"
            send_message(message)
            previous_status = current_status
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
