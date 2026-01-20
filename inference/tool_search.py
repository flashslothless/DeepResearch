import json
import os
from typing import List, Union, Optional
import requests
from qwen_agent.tools.base import BaseTool, register_tool


TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
TAVILY_API_URL = "https://api.tavily.com/search"


@register_tool("search", allow_overwrite=True)
class Search(BaseTool):
    name = "search"
    description = "Performs web searches using Tavily API: supply an array 'query'; the tool retrieves the top results for each query in one call."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Array of query strings. Include multiple complementary search queries in a single call."
            },
        },
        "required": ["query"],
    }

    def __init__(self, cfg: Optional[dict] = None):
        super().__init__(cfg)

    def tavily_search(self, query: str) -> str:
        """
        Perform a search using Tavily API.
        
        Args:
            query: The search query string
            
        Returns:
            Formatted search results as a string
        """
        if not TAVILY_API_KEY:
            return "[Search Error]: TAVILY_API_KEY environment variable not set."
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 10
        }
        
        for attempt in range(3):
            try:
                response = requests.post(
                    TAVILY_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                results = response.json()
                
                return self._format_results(query, results)
                
            except requests.exceptions.Timeout:
                if attempt == 2:
                    return f"[Search Error]: Timeout while searching for '{query}'. Please try again."
                continue
            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    return f"[Search Error]: Failed to search for '{query}': {str(e)}"
                continue
            except Exception as e:
                return f"[Search Error]: Unexpected error while searching for '{query}': {str(e)}"
        
        return f"[Search Error]: All attempts failed for '{query}'."

    def _format_results(self, query: str, results: dict) -> str:
        """
        Format Tavily API results into a readable string.
        
        Args:
            query: The original search query
            results: The JSON response from Tavily API
            
        Returns:
            Formatted string with search results
        """
        web_snippets = []
        
        # Include Tavily's generated answer if available
        answer = results.get("answer", "")
        
        # Process search results
        search_results = results.get("results", [])
        
        if not search_results:
            return f"No results found for '{query}'. Try with a more general query."
        
        for idx, result in enumerate(search_results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")
            
            # Build the formatted result
            snippet = f"{idx}. [{title}]({url})\n{content}"
            web_snippets.append(snippet)
        
        # Build final content
        content_parts = [f"A search for '{query}' found {len(web_snippets)} results:"]
        
        if answer:
            content_parts.append(f"\n## Quick Answer\n{answer}")
        
        content_parts.append("\n## Web Results\n" + "\n\n".join(web_snippets))
        
        return "\n".join(content_parts)

    def call(self, params: Union[str, dict], **kwargs) -> str:
        """
        Execute the search tool.
        
        Args:
            params: Either a JSON string or dict containing 'query' field
            
        Returns:
            Search results as a formatted string
        """
        try:
            if isinstance(params, str):
                params = json.loads(params)
            query = params.get("query", params.get("params", {}).get("query"))
        except Exception:
            return "[Search] Invalid request format: Input must be a JSON object containing 'query' field"
        
        if not query:
            return "[Search] Error: No query provided"
        
        if isinstance(query, str):
            # Single query
            response = self.tavily_search(query)
        else:
            # Multiple queries
            assert isinstance(query, List)
            responses = []
            for q in query:
                responses.append(self.tavily_search(q))
            response = "\n=======\n".join(responses)
        
        return response
