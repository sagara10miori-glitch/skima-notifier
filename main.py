from parse import fetch_items
from notify import send_notification
from storage.safe_json import load_seen_ids, save_seen_ids

def main():
    print("=== Notifier started ===")

    seen_ids = load_seen_ids()

    print("Fetching items...")
    items = fetch_items()

    if not items:
        print("No items found.")
        return

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

if __name__ == "__main__":
    main()
