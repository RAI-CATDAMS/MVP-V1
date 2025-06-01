
from plyer import notification

def show_alert(message):
    notification.notify(
        title="CATDAMS Sentinel Alert",
        message=message,
        timeout=5
    )
