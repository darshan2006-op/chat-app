""""
Main entry point for the client application.
This script initializes the GUI window and starts the event loop.
"""

# Import necessary modules
from gui import Window
import asyncio as aio

def main():
    """
    Main function to run the client application.
    This function initializes the GUI window and starts the event loop.
    """
    window = Window()
    window.run()

if __name__ == "__main__":
    main()