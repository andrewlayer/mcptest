from typing import Dict, Any, List
import httpx
from mcp import Tool

from parse import OpenAPIParser

class OpenAPIToolGenerator:
    @classmethod
    def from_parser(cls, parser: OpenAPIParser) -> 'OpenAPIToolGenerator':
        """Create tool generator from parser instance"""
        return cls(
            spec=parser.get_spec(),
            base_url=parser.get_base_url()
        )

    def __init__(self, spec: Dict[str, Any], base_url: str):
        self.spec = spec
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
 
    def generate_tools(self) -> List[Tool]:
        """Generate MCP tools from OpenAPI paths"""
        tools = []
        for path, path_item in self.spec.get('paths', {}).items():
            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    tool = self._create_tool(path, method, operation)
                    tools.append(tool)
        return tools

    def _create_tool(self, path: str, method: str, operation: Dict[str, Any]) -> Tool:
        """Create single tool from OpenAPI operation"""
        tool_name = f"{method.lower()}_{path.replace('/', '_')}"
        description = operation.get('summary', '') or operation.get('description', '')
        
        # Build input schema from parameters and requestBody
        input_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # Add path parameters
        for param in operation.get('parameters', []):
            param_name = param['name']
            input_schema['properties'][param_name] = {
                "type": param.get('schema', {}).get('type', 'string'),
                "description": param.get('description', '')
            }
            if param.get('required', False):
                input_schema['required'].append(param_name)

        # Add request body if present
        if 'requestBody' in operation:
            content = operation['requestBody'].get('content', {})
            if 'application/json' in content:
                body_schema = content['application/json'].get('schema', {})
                input_schema['properties']['body'] = body_schema
                if operation['requestBody'].get('required', False):
                    input_schema['required'].append('body')

        return Tool(
            name=tool_name,
            description=description,
            inputSchema=input_schema
        )