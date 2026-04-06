import logging
from typing import List, Dict, Any, Optional
from ddgs import DDGS
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# --- LLM Summarizer Abstraction ---

class BaseSummarizer(ABC):
    """
    Abstract base class for LLM summarizers.
    Implement this class to add support for different LLMs (e.g., LLaMA, OpenAI, Anthropic, Gemini).
    """
    @abstractmethod
    def summarize(self, query: str, search_results: List[Dict[str, str]]) -> str:
        """
        Summarize the search results based on the query.
        
        Args:
            query (str): The search query.
            search_results (List[Dict[str, str]]): List of search results (usually contains 'title', 'body', 'href').
            
        Returns:
            str: The generated summary.
        """
        pass


class LLaMASummarizer(BaseSummarizer):
    """
    Placeholder implementation for a LLaMA-based summarizer.
    """
    def __init__(self, model_path: Optional[str] = None, api_key: Optional[str] = None):
        # Initialize LLaMA model locally or via API
        self.model_path = model_path
        self.api_key = api_key
        
    def summarize(self, query: str, search_results: List[Dict[str, str]]) -> str:
        # Construct a prompt for the LLM
        context = ""
        for i, res in enumerate(search_results, start=1):
            title = res.get('title', 'No Title')
            body = res.get('body', 'No Content')
            link = res.get('href', 'No Link')
            context += f"Result {i}:\nTitle: {title}\nSummary: {body}\nLink: {link}\n\n"
            
        prompt = (
            f"Please summarize the following search results to answer the query: '{query}'\n\n"
            f"Search Results:\n{context}\n"
            f"Summary:"
        )
        
        # TODO: Replace with actual LLaMA inference code
        logger.info("Using LLaMASummarizer to generate summary.")
        dummy_summary = f"[LLaMA Summary Placeholder for query '{query}']: Found {len(search_results)} relevant results. (Implement LLaMA inference here)"
        return dummy_summary

# You can easily add other summarizers like:
# class OpenAISummarizer(BaseSummarizer):
#     def summarize(self, query: str, search_results: List[Dict[str, str]]) -> str: ...


# --- Web Search Implementation ---

class WebSearch:
    """
    Main class to handle Web Search and integration with a Summarizer.
    """
    def __init__(self, summarizer: Optional[BaseSummarizer] = None):
        """
        Initialize the WebSearch tool.
        
        Args:
            summarizer (BaseSummarizer, optional): The LLM summarizer to use. 
                                                   If None, LLaMASummarizer will be used by default.
        """
        self.summarizer = summarizer or LLaMASummarizer()
        
    def set_summarizer(self, summarizer: BaseSummarizer):
        """Allows switching the LLM summarizer on the fly."""
        self.summarizer = summarizer
        
    def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query (str): The search query.
            limit (int): Maximum number of results to return.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing 'title', 'href', and 'body'.
        """
        results = []
        try:
            with DDGS() as ddgs:
                ddg_results = ddgs.text(query, max_results=limit)
                if ddg_results:
                    results = list(ddg_results)
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {e}")
            
        return results
        
    def search_and_summarize(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Perform a web search and then summarize the results using the configured LLM.
        
        Args:
            query (str): The search query.
            limit (int): Maximum number of results to fetch for the summary.
            
        Returns:
            Dict[str, Any]: A dictionary containing the 'query', 'summary', and raw 'results'.
        """
        logger.info(f"Performing search for query: '{query}'")
        search_results = self.search(query, limit=limit)
        
        if not search_results:
            return {
                "query": query,
                "summary": "No search results found.",
                "results": []
            }
            
        logger.info("Generating summary for search results...")
        summary = self.summarizer.summarize(query, search_results)
        
        return {
            "query": query,
            "summary": summary,
            "results": search_results
        }

if __name__ == "__main__":
    # Example usage:
    logging.basicConfig(level=logging.INFO)
    
    # Instantiate WebSearch (uses default LLaMASummarizer)
    web_search = WebSearch()
    
    query = "What are the latest advancements in artificial intelligence?"
    response = web_search.search_and_summarize(query, limit=3)
    
    print("\n--- QUERY ---")
    print(response["query"])
    print("\n--- SUMMARY ---")
    print(response["summary"])
    print("\n--- RAW RESULTS ---")
    for r in response["results"]:
        print(f"- {r.get('title')}: {r.get('href')}")
