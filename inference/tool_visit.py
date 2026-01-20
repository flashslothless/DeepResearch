import json
import os
from typing import List, Union, Optional
import requests
from qwen_agent.tools.base import BaseTool, register_tool


TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
TAVILY_EXTRACT_URL = "https://api.tavily.com/extract"


@register_tool("visit", allow_overwrite=True)
class Visit(BaseTool):
    name = 'visit'
    description = 'Visit webpage(s) and return the content. Uses Tavily extract API.'
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": ["string", "array"],
                "items": {"type": "string"},
                "description": "The URL(s) of the webpage(s) to visit. Can be a single URL or an array of URLs."
            },
            "goal": {
                "type": "string",
                "description": "The specific information goal for visiting webpage(s)."
            }
        },
        "required": ["url", "goal"]
    }

    def __init__(self, cfg: Optional[dict] = None):
        super().__init__(cfg)

    def tavily_extract(self, urls: List[str], goal: str) -> str:
        """
        Extract content from URLs using Tavily extract API.
        
        Args:
            urls: List of URLs to extract content from
            goal: The user's goal for extraction (used for reranking)
            
        Returns:
            Extracted content as formatted string
        """
        if not TAVILY_API_KEY:
            return "[Visit Error]: TAVILY_API_KEY environment variable not set."
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": TAVILY_API_KEY,
            "urls": urls,
            "extract_depth": "basic",  # Use basic for faster response, can be "advanced"
            "include_images": False
        }
        
        for attempt in range(3):
            try:
                response = requests.post(
                    TAVILY_EXTRACT_URL,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                results = response.json()
                
                return self._format_extract_results(results, goal)
                
            except requests.exceptions.Timeout:
                if attempt == 2:
                    return f"[Visit Error]: Timeout while extracting content from URLs."
                continue
            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    return f"[Visit Error]: Failed to extract content: {str(e)}"
                continue
            except Exception as e:
                return f"[Visit Error]: Unexpected error: {str(e)}"
        
        return "[Visit Error]: All attempts failed."

    def _format_extract_results(self, results: dict, goal: str) -> str:
        """
        Format Tavily extract API results into a readable string.
        
        Args:
            results: The JSON response from Tavily extract API
            goal: The user's goal for context
            
        Returns:
            Formatted string with extracted content
        """
        output_parts = []
        
        # Process successful extractions
        extracted_results = results.get("results", [])
        failed_results = results.get("failed_results", [])
        
        if not extracted_results and failed_results:
            failed_urls = [f.get("url", "unknown") for f in failed_results]
            return f"[Visit Error]: Failed to extract content from: {', '.join(failed_urls)}"
        
        for result in extracted_results:
            url = result.get("url", "Unknown URL")
            raw_content = result.get("raw_content", "")
            
            # Truncate content if too long
            max_content_length = 50000
            if len(raw_content) > max_content_length:
                raw_content = raw_content[:max_content_length] + "\n... [content truncated]"
            
            output_parts.append(f"## Content from {url}\n\n{raw_content}")
        
        if not output_parts:
            return "[Visit Error]: No content could be extracted from the provided URLs."
        
        # Add goal context
        header = f"Extracted content for goal: {goal}\n\n"
        return header + "\n\n---\n\n".join(output_parts)

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """
        Execute the visit tool.
        
        Args:
            params: Either a JSON string or dict containing 'url' and 'goal' fields
            
        Returns:
            Extracted webpage content as a formatted string
        """
        try:
            if isinstance(params, str):
                params = json.loads(params)
            
            # Handle nested params structure
            if "params" in params:
                params = params["params"]
            
            url = params.get("url", [])
            goal = params.get("goal", "Extract relevant information")
        except Exception as e:
            return f"[Visit] Invalid request format: {str(e)}"
        
        if not url:
            return "[Visit] Error: No URL provided"
        
        # Normalize url to list
        if isinstance(url, str):
            urls = [url]
        else:
            urls = url
        
        # Filter out invalid URLs
        valid_urls = [u for u in urls if u.startswith(("http://", "https://"))]
        
        if not valid_urls:
            return "[Visit] Error: No valid URLs provided (must start with http:// or https://)"
        
        print(f"[Visit] Extracting content from {len(valid_urls)} URL(s) using Tavily...")
        
        return self.tavily_extract(valid_urls, goal)