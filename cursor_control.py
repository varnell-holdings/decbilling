import win32api
import time


def disable_mouse():
    # Set clip area to a 1x1 pixel (effectively disabling mouse)
    win32api.ClipCursor((0, 0, 1, 1))
    print("Mouse disabled")


def enable_mouse():
    # Remove all cursor restrictions
    win32api.ClipCursor(None)
    print("Mouse enabled")


# Example usage
if __name__ == "__main__":
    disable_mouse()
    try:
        print("Running your program...")
        # Your program code here
        time.sleep(5)  # Simulate program running for 5 seconds
    finally:
        # Always re-enable the mouse
        enable_mouse()
