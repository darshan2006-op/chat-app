"""
This script is was meant to test the client side logic to connect to the server and send messages.
"""

# Import necessary modules
import socket as soc
import asyncio as aio

# Initialize the client socket
client = soc.socket(soc.AF_INET, soc.SOCK_STREAM)

# Connect to the server
client.connect((soc.gethostbyname(soc.gethostname()), 8080))
client.setblocking(False)

async def read_data():
    """ 
    A function to read data from the client socket asynchronously.
    It attempts to read data from the socket and prints it to the console.
    """
    try:
        # Attempt to read data from the client socket
        data = client.recv(1024)
        print(f"Received: {data.decode()}")
    except BlockingIOError:
        # If the socket is not ready to read data, we simply return
        return
    except Exception as e:
        # Handle any other exceptions that may occur during reading
        print(f"An error occurred while reading data: {e}")
        return

async def main():
    """
    Main function to run the test client application.
    This function connects to the server, sends messages in a loop, and reads responses asynchronously.
    """

    # Initialize a counter to keep track of the number of messages sent
    i = 0

    # Loop to send messages to the server
    # The loop will run until 10 messages are sent or an error occurs
    while i < 10:
        try:
            # Send a message to the server with a counter and an EOF marker
            client.sendall(f"Message no {i}<EOF>".encode())

            # Create a task to read data from the server asynchronously
            aio.create_task(read_data())

            # Wait for 2 seconds before sending the next message
            await aio.sleep(2)
        except BlockingIOError:
            # If the socket is not ready to send data, we simply wait and retry
            print("Socket is currently blocking, retrying...")
            await aio.sleep(0)
        except Exception as e:
            # Handle any other exceptions that may occur during sending
            print(f"An error occurred: {e}")
            break
        finally:
            i += 1
    
    # Close the client socket after sending all messages
    client.close()

if __name__ == "__main__":
    # Run the main function using asyncio's event loop
    aio.run(main())