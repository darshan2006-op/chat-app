"""
This module implements a GUI client using Tkinter and asyncio.
It connects to a server socket, allows users to send messages, and displays incoming messages in a text area.
"""

# Import necessary libraries
from tkinter import *
import asyncio as aio
import socket as soc

class Window(Tk):
    """
    A class that packages the gui functionality and the socket client.
    """

    def __init__(self):
        """
        Initializes the Window class, sets up the window, and connects to the server socket,
        run the asyncio event loop to handle incoming messages,
        also sets up the necessary widgets for sending and displaying messages.
        """
        # Initialize the Tkinter window
        super().__init__()
        self.title("Simple GUI")
        self.geometry("600x500+200+200")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.running = aio.Event()

        # Connect to the server socket
        self.connect()

        # Create widgets for the GUI
        self.make_widgets()

        # Initialize the asyncio event loop and start reading messages
        self.loop = aio.new_event_loop()
        self.running_task = aio.run_coroutine_threadsafe(self.read(), self.loop)
        self.run_loop()

    def send_message(self):
        """
        Sends a message from the message box to the server socket.
        """
        # Get the message from the message box, append an EOF marker, and send it to the server
        message = self.msg_box.get()

        # Check if the message is not empty before sending
        if message != "":
            try:
                # Append EOF marker to the message and send it
                msg = message + "<EOF>"
                print(f"Sending message: {msg}")
                # Send the message to the server socket
                print(self.client_socket.send(msg.encode('utf-8')))
                # Clear the message box and update the display area
                self.msg_box.delete(0, END)
                self.msg_display.insert(END, f"You: {message}\n")
            except Exception as e:
                # Handle any exceptions that occur during sending
                print(f"Error sending message: {e}")

    def run_loop(self):
        """
        Runs the asyncio event loop to handle incoming messages.
        This method is called periodically to ensure the event loop is running.
        """
        try:
            # Run the asyncio event loop for a short duration to process incoming messages
            self.loop.run_until_complete(aio.sleep(0))
        except Exception as e:
            pass

        # Schedule the next run of the event loop
        self.after(10, self.run_loop)

    def connect(self):
        """
        Connects to the server socket at the specified address and port.
        """

        self.client_socket = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
        self.client_socket.connect((soc.gethostbyname(soc.gethostname()), 8080))
        self.client_socket.setblocking(False)
        print("Connected to server")

    def destroy(self):
        """
        Handles the window close event, cancels the running task, and cleans up resources.
        """

        print("Window closed")
        self.running.set()
        self.client_socket.close()
        super().destroy()
    
    def run(self):
        """
        Starts the main event loop of the Tkinter window.
        """
        try:
            self.mainloop()
        finally:
            # Ensure the asyncio loop is stopped and the running task is cancelled
            if self.running_task:
                self.running_task.cancel()
            self.loop.close()

    async def read(self):
        """
        Asynchronously reads messages from the server socket and displays them in the text area.
        This method runs in a loop until the connection is closed or an error occurs.
        """

        print("Starting to read messages...")
        # Run until the running event is set
        while not self.running.is_set():
            try:
                # Attempt to read a message from the server socket
                msg = self.client_socket.recv(1024)

                # If a message is received, decode it and insert it into the text area
                if msg != b'':
                    self.msg_display.insert(END, msg.decode('utf-8').replace('<EOF>', '') + '\n')
                # If server closes the connection, break the loop
                else:
                    print("Connection closed by server")
                    self.running.set()
                    break
            except soc.error as e:
                # Handle socket errors, specifically connection reset by peer
                if e.errno == 10054:
                    self.running.set()
                    break
            except BlockingIOError:
                # Handle the case where no data is available to read
                await aio.sleep(0)
            except aio.CancelledError:
                # Handle cancellation of the coroutine
                break
            except Exception as e:
                # Handle any other exceptions that may occur
                print(f"Error reading message: {e}")
            finally:
                # Ensure the event loop yields control to allow other tasks to run
                await aio.sleep(0)

    def _do_nothing(self, event):
        """
        A placeholder method that does nothing.
        This can be used to override default behaviors or for future extensions.

        args:
            event: The event that triggered this method, typically not used.
        
        Returns:
            None
        """
        return "break"

    def make_widgets(self):
        """
        Creates the necessary widgets for the GUI, including the message box,
        send button, and the text area for displaying messages.
        """
        # make the bottom frame
        self.bottom_frame = Frame(self)
        self.bottom_frame.pack(side=BOTTOM, fill=X, anchor='s', ipadx=10, ipady=5)

        self.msg_box = Entry(self.bottom_frame)
        self.msg_box.pack(side=LEFT, fill=X, expand=True, padx=5)

        self.send_button = Button(self.bottom_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=RIGHT, fill=X, padx=5, ipadx=50)

        # main area
        self.frame = Frame(self)
        self.frame.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=10)

        self.msg_display = Text(self.frame, bg="white", fg="black", wrap=WORD)
        self.msg_display.bind("<Key>", self._do_nothing)
        self.msg_display.bind("<Button-2>", self._do_nothing)
        self.msg_display.bind("<Control-v>", self._do_nothing)
        self.msg_display.pack(side=LEFT, fill=BOTH, expand=True)
