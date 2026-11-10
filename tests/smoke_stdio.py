"""End-to-end: start the server over stdio like an AI client would and call a tool."""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main(cmd):
    params = StdioServerParameters(command=cmd[0], args=cmd[1:])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = [t.name for t in (await s.list_tools()).tools]
            print("tools:", tools)
            res = await s.call_tool("cheapest", {"market": "spot", "side": "taker", "top": 3})
            print(res.content[0].text[:600])


asyncio.run(main(sys.argv[1:]))
