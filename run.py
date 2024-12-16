from typing import Sequence
import debugpy
from h11 import Request
from mcp import Tool
from mcp.types import Resource, ResourceTemplate, Prompt, PromptArgument, GetPromptResult, PromptMessage, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

# Create SSE transport with endpoint
sse = SseServerTransport("/messages")
app = Server("test")

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, str] | None) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    result = f"Calculated result: {arguments}"  
    return [TextContent(type="text", text=result)]

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "required": ["a", "b"],
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number to add"
                    },
                    "b": {
                        "type": "number", 
                        "description": "Second number to add"
                    }
                }
            }
        )
    ]
        

@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str]) -> Prompt:
    return GetPromptResult(
        description="A sample prompt response",
        messages=[
            PromptMessage(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=f"This is a sample prompt response {arguments}"
                )
            )
        ]
    )

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="name",
            description="Your name",
            arguments=[
                PromptArgument(
                    name="name",
                    description="Your name",
                    required=True
                )
            ]
        )
    ]

@app.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file:///home/user/documents/report.pdf",
            name="Report Document",
            description="A PDF report document",
            mimeType="application/pdf"
        ),
        Resource(
            uri="file:///home/user/images/photo.jpg",
            name="Sample Photo",
            description="A sample JPEG photo",
            mimeType="image/jpeg"
        ),
        Resource(
            uri="http://example.com/api/data",
            name="API Data",
            description="Data from example API",
            mimeType="application/json"
        ),
        Resource(
            uri="screen://localhost/display1",
            name="Screen Capture",
            description="Current screen capture",
            mimeType="image/png"
        ),
        Resource(
            uri="postgres://database/customers/schema",
            name="Customer Database Schema",
            description="Schema of the customer database",
            mimeType="application/sql"
        )
    ]

@app.list_resource_templates()
async def list_resource_templates() -> list[Resource]:
    return [
        ResourceTemplate(
            uriTemplate="weather://{name}",
            name="Weather Template",
            description="Getting the weather",
            mimeType="application/json"
        )
    ]
    

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    
    if str(uri).startswith("weather://"):
        return f"This is a weather resource {uri}"
        
    return f"This is resource {uri}"

# Handler for SSE connections
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )

# Handler for client messages
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/messages", handle_messages, methods=["POST"]),
        Route("/sse", handle_sse, methods=["GET"]),
    ]
)

if __name__ == "__main__":
    
    debugpy.listen(("0.0.0.0", 5679))
    
    uvicorn.run(
        "run:starlette_app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_dirs=["./"]  
    )