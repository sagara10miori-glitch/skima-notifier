import time
from parse import fetch_items
from notify import send_notification
from storage.safe_json import load_seen_ids, save_seen_ids
from config.settings import CHECK_INTERVAL

def main():
    print("=== Notifier started ===")

    seen_ids = load_seen_ids()

    while True:
        print("Fetching items...")
        items = fetch_items()

        if not items:
            print("No items found. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        new_items = [item for item in items if item["id"] not in seen_ids]

        if new_items:
            print(f"Found {len(new_items)} new items.")

            for item in new_items:
                print(f"Sending notification for: {item['title']}")
                send_notification(item)
                seen_ids.append(item["id"])

            save_seen_ids(seen_ids)
        else:
            print("No new items.")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
