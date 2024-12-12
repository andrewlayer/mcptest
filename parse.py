import yaml
import json
from pathlib import Path
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAPIParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.spec = self._load_spec()
        
    def _load_spec(self) -> Dict[str, Any]:
        """Load and validate YAML file"""
        try:
            suffix = self.file_path.suffix.lower()
            with open(self.file_path, 'r') as f:
                if suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif suffix == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {suffix}. Use .yaml, .yml, or .json")
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise

    def print_server_info(self):
        """Print server information"""
        print("\nApplication servers:")
        for server in self.spec.get('servers', []):
            print(f"  {server.get('description', 'No description')} - {server.get('url', 'No URL')}")

    def print_paths(self):
        """Print API paths"""
        print("\nAPI Paths:")
        for path, details in self.spec.get('paths', {}).items():
            print(f"\n{path}:")
            for method, operation in details.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    print(f"  {method.upper()}: {operation.get('summary', 'No summary')}")

    def print_schemas(self):
        """Print schema definitions"""
        print("\nSchemas:")
        schemas = self.spec.get('components', {}).get('schemas', {})
        for name, schema in schemas.items():
            print(f"\n{name}:")
            required = schema.get('required', [])
            if required:
                print(f"  Required: {', '.join(required)}")
            properties = schema.get('properties', {})
            print("  Properties:")
            for prop, details in properties.items():
                print(f"    - {prop}: {details.get('type', 'No type')}")
                
    def get_base_url(self) -> str:
        """Get first server URL from spec"""
        servers = self.spec.get('servers', [])
        if servers:
            return servers[0].get('url', '')
        return ''

    def get_spec(self) -> Dict[str, Any]:
        """Get validated OpenAPI spec"""
        return self.spec

if __name__ == "__main__":
    try:
        parser = OpenAPIParser('./neon.json')
        parser.print_server_info()
        parser.print_paths()
        # parser.print_schemas()
    except Exception as e:
        logger.error(f"Failed to parse OpenAPI specification: {e}")