#!/usr/bin/env python3
# Basic load balance proxy server example

import argparse
import asyncio
import random
from typing import List

async def forward_request(reader, writer, target_host: str, target_port: int):
    """Forward request to target host."""
    try:
        target_reader, target_writer = await asyncio.open_connection(
            target_host, target_port
        )
        # Forward data bidirectionally
        while True:
            data = await reader.read(4096)
            if not data:
                break
            target_writer.write(data)
            await target_writer.drain()

            response = await target_reader.read(4096)
            if not response:
                break
            writer.write(response)
            await writer.drain()
    except Exception as e:
        print(f"Error forwarding request: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_client(reader, writer, prefiller_hosts: List[str], prefiller_ports: List[int],
                        decoder_hosts: List[str], decoder_ports: List[int]):
    """Handle client connection with round-robin load balancing."""
    # Simple round-robin: alternate between prefillers
    idx = random.randint(0, len(prefiller_hosts) - 1)
    target_host = prefiller_hosts[idx]
    target_port = prefiller_ports[idx]

    await forward_request(reader, writer, target_host, target_port)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000, help="Proxy server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Proxy server host")
    parser.add_argument("--prefiller-hosts", nargs="+", required=True, help="Prefiller hosts")
    parser.add_argument("--prefiller-ports", nargs="+", type=int, required=True, help="Prefiller ports")
    parser.add_argument("--decoder-hosts", nargs="+", required=True, help="Decoder hosts")
    parser.add_argument("--decoder-ports", nargs="+", type=int, required=True, help="Decoder ports")

    args = parser.parse_args()

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, args.prefiller_hosts, args.prefiller_ports,
                                   args.decoder_hosts, args.decoder_ports),
        args.host, args.port
    )

    print(f"Proxy server running on {args.host}:{args.port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())