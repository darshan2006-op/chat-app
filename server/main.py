"""
This is a asynchronous socket server that handles multiple client connections.
It allows clients to send messages to each other, and broadcasts messages to all connected clients except the sender.
It uses asyncio for asynchronous operations and non-blocking sockets to handle multiple clients concurrently.
"""

# import necessary modules
import asyncio as aio
import socket as soc

# Initilize the server socket and a list to keep track of connected clients
server = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
clients: list[soc.socket] = []

async def readAll(client_socket: soc.socket) -> tuple[bytes, bool]:
    """ 
    A function to read all the messages from a client socket until it receives a message ending with <EOF>.

    Args:
        client_socket (soc.socket): The socket object for the client connection.
    
    Returns:
        tuple[bytes, bool]: A tuple containing the received data and a boolean indicating if the client is still connected.
        if the client is still connected, the boolean will be True, otherwise it will be False.
        data will be the bytes received from the client or None if the data to be read is not ready.
    """

    # initialize an empty bytes object to store the received data
    data = b""

    # Use a loop to continuously read data from the client socket
    # until it receives a message ending with <EOF> or the client disconnects or an error occurs
    while True:
        try:
            # Try to receive data from the client socket
            chunk = client_socket.recv(1024)

            # Append the received chunk to the data
            data += chunk

            # If the chunk is empty, it means the client has disconnected 
            # and we return the data received so far and False to indicate disconnection
            if chunk == b'':
                return data, False

            # If the received data ends with <EOF>, return the data and True to indicate the client is still connected
            if data.endswith(b'<EOF>'):
                return data, True
            

        except BlockingIOError:
            # If the socket is not ready to read data, return None and True
            # to indicate that the client is still connected but no data is available at the moment
            return None, True
        except Exception as e:
            # Handle any other exceptions that may occur during reading
            print(f"Error while reading messages: {e}")
            return None, False

async def broadcast(message: bytes, sender: soc.socket) -> None:
    """
    a function to handle the task of broadcasting a message to all connected clients except the sender.
    
    Args:
        message (bytes): The message to broadcast.
        sender (soc.socket): The socket of the client that sent the message.

    Returns:
        None
    """
    # Referencing the global clients list to access connected clients
    global clients

    # Check if there are at least two clients connected
    if len(clients) < 2:
        return

    # Prepend the sender's address to the message and encode it
    message = str(sender.getpeername()).encode() + b": " + message

    # Iterate through the list of clients and send the message to each one
    for client in clients[:]:
        try:
            # Skip the sender to avoid sending the message back to the client that sent it
            if client == sender:
                continue

            # Send the message to the client
            client.sendall(message)
        except BrokenPipeError:
            # Handle the case where the client has disconnected
            print(f"Client {client.getpeername()} disconnected.")
            clients.remove(client)
        except BlockingIOError:
            # If the socket is not ready to send data, yield control to the event loop
            await aio.sleep(0)
        except Exception as e:
            # Handle any other exceptions that may occur during broadcasting
            print(f"Error while broadCasting {client.getpeername()}: {e}")
            clients.remove(client)

async def handle_client(client_socket: soc.socket, add: soc.AddressInfo) -> None:
    """
    Handle client connections and manage communication between them.
    
    Args:
        client_socket (soc.socket): The socket object for the client connection.
        add (soc.AddressInfo): The address information of the client.
    
    Returns:
        None
    """
    global clients
    client_socket.setblocking(False)
    clients.append(client_socket)
    connected = True
    while connected:
        try:
            data, conn = await readAll(client_socket)
            if not conn:
                connected = False
            if data :
                print(f"Received from {add}: {data}")
                aio.create_task(broadcast(data, client_socket))
            await aio.sleep(0)  # Yield control to the event loop
        except Exception as e:
            print(f"error while handling client: {e}")
            break
    print(f"client {add} disconnected.")
    print(f"length of clients: {len(clients)}")
    clients.remove(client_socket)
    client_socket.close()

async def main() -> None:
    """Main function to set up the server and handle incoming connections."""

    # Print initialization messages and details
    print(f"Starting the server on {soc.gethostbyname(soc.gethostname())}...")

    # Get the current host to run the server and bind to port 8080
    bind_address = (soc.gethostbyname(soc.gethostname()), 8080)
    server.bind(bind_address)

    # Set blocking to False to allow non-blocking operations 
    server.setblocking(False)

    # Start listening for incoming connections
    server.listen()

    # Connection handling loop
    while True:
        try:
            # Try to accept a new client connection
            client_socket, addr = server.accept()
            print(f"Connection from {addr} has been established.")
            
            # Create a new task to handle the client connection
            aio.create_task(handle_client(client_socket, addr))
        except BlockingIOError:
            # If no connections are available, yield control to the event loop
            await aio.sleep(0)
        except Exception as e:
            # Handle any other exceptions that may occur
            print(f"Error in the mainloop: {e}")
            break

if __name__ == "__main__":
    aio.run(main())