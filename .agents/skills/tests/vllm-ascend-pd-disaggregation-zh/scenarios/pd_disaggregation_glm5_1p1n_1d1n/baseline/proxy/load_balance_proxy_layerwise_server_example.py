#!/usr/bin/env python3
# Layerwise load balance proxy server example

import argparse
import asyncio
from typing import List, Dict
import json

class LayerwiseProxy:
    """Proxy with layerwise KV cache management."""

    def __init__(self, prefiller_hosts: List[str], prefiller_ports: List[int],
                 decoder_hosts: List[str], decoder_ports: List[int]):
        self.prefiller_hosts = prefiller_hosts
        self.prefiller_ports = prefiller_ports
        self.decoder_hosts = decoder_hosts
        self.decoder_ports = decoder_ports
        self.prefiller_index = 0
        self.decoder_index = 0

    def get_next_prefiller(self):
        """Get next prefiller using round-robin."""
        host = self.prefiller_hosts[self.prefiller_index]
        port = self.prefiller_ports[self.prefiller_index]
        self.prefiller_index = (self.prefiller_index + 1) % len(self.prefiller_hosts)
        return host, port

    def get_next_decoder(self):
        """Get next decoder using round-robin."""
        host = self.decoder_hosts[self.decoder_index]
        port = self.decoder_ports[self.decoder_index]
        self.decoder_index = (self.decoder_index + 1) % len(self.decoder_hosts)
        return host, port

async def forward_request(reader, writer, target_host: str, target_port: int):
    """Forward request to target host."""
    try:
        target_reader, target_writer = await asyncio.open_connection(
            target_host, target_port
        )
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

async def handle_client(reader, writer, proxy: LayerwiseProxy):
    """Handle client connection with layerwise routing."""
    # Route to prefiller first, then to decoder
    target_host, target_port = proxy.get_next_prefiller()
    await forward_request(reader, writer, target_host, target_port)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1999, help="Proxy server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Proxy server host")
    parser.add_argument("--prefiller-hosts", nargs="+", required=True, help="Prefiller hosts")
    parser.add_argument("--prefiller-ports", nargs="+", type=int, required=True, help="Prefiller ports")
    parser.add_argument("--decoder-hosts", nargs="+", required=True, help="Decoder hosts")
    parser.add_argument("--decoder-ports", nargs="+", type=int, required=True, help="Decoder ports")

    args = parser.parse_args()

    proxy = LayerwiseProxy(args.prefiller_hosts, args.prefiller_ports,
                           args.decoder_hosts, args.decoder_ports)

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, proxy),
        args.host, args.port
    )

    print(f"Layerwise proxy server running on {args.host}:{args.port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())