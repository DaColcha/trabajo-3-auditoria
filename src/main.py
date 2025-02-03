import os
import sys
from datetime import datetime
import tkinter as tk
from connection import connection_gui

def main():
    print(f"Application started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"User: {os.getenv('USERNAME')}")
    connection_gui.mainloop()

if __name__ == "__main__":
    main()