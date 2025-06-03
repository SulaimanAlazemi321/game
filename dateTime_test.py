from datetime import datetime, UTC

with open('timestamps.txt', "a") as f:
    timestamp = datetime.now(UTC)
    f.writelines(f"{timestamp.isoformat()}\n")