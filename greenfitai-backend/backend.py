#!/usr/bin/env python
import asyncio
import websockets
import ssl
import os
from chatUtils import reply

async def echo(websocket):
    try:
        print("New connection established", flush=True)
        async for message in websocket:
            chatbotmessage = reply(message)
            await websocket.send(chatbotmessage)
            await websocket.send("[END]")
            print("Sent response", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error details: {str(e)}", flush=True)
        print(f"Error type: {type(e)}", flush=True)


async def main():
    print("WebSocket server starting", flush=True)

    # SSL/TLS context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # Use TLS for security

    # Load the certificate and private key
    ssl_context.load_cert_chain("/run/secrets/certificate", "/run/secrets/privatekey")

    server = await websockets.serve(
        echo,
        "0.0.0.0",
        int(os.environ.get('PORT', 443)),
        ssl=ssl_context # Pass the SSL context
    )
    print(f"WebSocket server running on port {os.environ.get('PORT', 8090)}", flush=True)
    await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Server startup error: {str(e)}", flush=True)