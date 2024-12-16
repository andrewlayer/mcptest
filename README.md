# MCP HTTP Server

This project shows MCP Server support using HTTP transport mechanism. I personally love learning about protocols by placing breakpoints in the code, and looking at the raw payloads being sent back and forth.  This project is a simple HTTP server that supports the MCP protocol.  This **only** works with the **inspector tool** at the moment, most clients do not support the HTTP transport mechanism yet.

## Setup

1. Install dependencies:
`pip install -r requirements.txt`

2. Run the server:
`python run.py`

3. Connect to server using HTTP transport mechanism in inspector tool.  ([Inspector Tool setup](https://modelcontextprotocol.io/docs/tools/inspector))
- `npx @modelcontextprotocol/inspector`
- The inspector tool runs on http://localhost:5173 🚀
- Click on the connect button and enter the URL of the server http://localhost:8000/sse

![Inspector Tool](connect.png)

4. Congrats! You are now connected to the server.  You can now send and receive messages using the inspector tool. Hit any of the buttons like `list resources` or `get resource` to see the server in action.  All responses are dummy responses.

# TODO:
- [ ] Implement sampling (this is a sick feature btw)



# Known Issues
For some reason the Hot Reload on this server is not working properly (The server hangs waiting).  Just restart the server and it will start up again (Or fix it, submit a PR and you will be my hero).