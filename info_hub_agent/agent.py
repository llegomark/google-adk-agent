from typing import Optional, List, Dict
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from bs4 import BeautifulSoup

from google.adk.agents import Agent
from google.adk.tools import google_search, agent_tool


def get_hackernews_posts(number_of_posts: Optional[int] = None):
    """
    Gets the top hackernews posts and extracts top post titles and links.

    Args:
        number_of_posts: The number of posts to return. If None, returns all posts.

    Returns:
        dict: status and result. In case of success, it contains a posts field with a
        list of dictionaries, where each dictionary contains the 'title' and 'link' of a post.
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        res = requests.get("https://news.ycombinator.com/", headers=headers)

        soup = BeautifulSoup(res.content, "html.parser")

        posts = []

        # Find all table rows with class 'athing' - these contain the posts
        post_rows = soup.find_all("tr", class_="athing")

        for row in post_rows:
            # Find the span with class 'titleline' within the row
            title_span = row.find("span", class_="titleline")

            if title_span:
                # Find the anchor tag (<a>) within the title span
                link_tag = title_span.find("a")
                if link_tag and link_tag.has_attr("href"):
                    title = link_tag.get_text(strip=True)
                    link = link_tag["href"]
                    posts.append({"title": title, "link": link})

        if number_of_posts is not None:
            posts = posts[:number_of_posts]

        return {
            "status": "success",
            "posts": posts,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error when trying to get hackernews posts: {e}",
        }


def get_github_trending_repos(number_of_repos: Optional[int] = None):
    """
    Gets the trending github repos and extracts repo name and link.

    Args:
        number_of_repos: The number of repos from the trending page to return. If None, returns all repos.

    Returns:
        dict: status and result. In case of success, it contains a repos field with a
        list of dictionaries, where each dictionary contains the 'title' and 'link' of a post.
    """

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        res = requests.get("https://github.com/trending", headers=headers)

        soup = BeautifulSoup(res.content, "html.parser")
        repos = []

        # Find all article elements which contain repository info
        # Updated selector based on the provided HTML structure
        repo_articles = soup.find_all("article", class_="Box-row")

        for article in repo_articles:
            # Find the h2 tag containing the link
            h2_tag = article.find("h2", class_="h3")
            if not h2_tag:
                continue  # Skip if structure is unexpected

            link_tag = h2_tag.find("a")
            if link_tag and link_tag.has_attr("href"):
                relative_link = link_tag["href"]
                full_link = f"https://github.com{relative_link}"

                # Extract and clean the title text (owner / repo_name)
                # Use .stripped_strings to get text parts and join them
                title_parts = list(link_tag.stripped_strings)
                if len(title_parts) >= 2:
                    # Join the parts, assuming the format is like ['owner', '/', 'repo_name']
                    # or just ['owner / repo_name'] after stripping
                    title = " ".join(title_parts).replace(
                        " ", ""
                    )  # Aims for "owner/repo_name"
                else:
                    title = (
                        link_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
                    )

                repos.append({"title": title, "link": full_link})

        if number_of_repos is not None:
            repos = repos[:number_of_repos]

        return {
            "status": "success",
            "repos": repos,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error when trying to get trending repos: {e}",
        }


def get_deped_rss_feed(max_items: Optional[int] = 10) -> Dict:
    """
    Fetches and parses the DepEd RSS feed.

    Args:
        max_items: Maximum number of items to return. Default is 10.

    Returns:
        dict: status and results. In case of success, it contains a 'feed_info' field with
        channel information and a 'items' field with a list of news items.
    """
    try:
        # Set request headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.deped.gov.ph/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Fetch the RSS feed with headers and allow redirects
        response = requests.get(
            "https://www.deped.gov.ph/feed/", 
            headers=headers, 
            allow_redirects=True,
            timeout=10
        )
        
        if response.status_code != 200:
            # Try alternate URL
            alternate_url = "https://www.deped.gov.ph/feed"
            response = requests.get(
                alternate_url,
                headers=headers,
                allow_redirects=True,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error_message": f"Failed to fetch RSS feed. Status code: {response.status_code}"
                }
        
        # Parse the XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            # Try to clean the XML content if parsing fails
            cleaned_content = response.content.decode('utf-8', errors='ignore')
            cleaned_content = cleaned_content.encode('utf-8')
            try:
                root = ET.fromstring(cleaned_content)
            except ET.ParseError as e:
                return {
                    "status": "error",
                    "error_message": f"Failed to parse RSS feed XML: {str(e)}"
                }
        
        # Get channel information
        channel = root.find("channel")
        if channel is None:
            return {
                "status": "error",
                "error_message": "Invalid RSS feed format (no channel element found)"
            }
            
        feed_info = {
            "title": channel.find("title").text if channel.find("title") is not None else "",
            "link": channel.find("link").text if channel.find("link") is not None else "",
            "description": channel.find("description").text if channel.find("description") is not None else "",
            "last_build_date": channel.find("lastBuildDate").text if channel.find("lastBuildDate") is not None else "",
        }
        
        # Get items
        items = []
        for item in channel.findall("item")[:max_items]:
            # Parse publication date
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            # Try to parse date to a nicer format
            try:
                dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
            except Exception:
                formatted_date = pub_date
            
            # Extract description and clean it up
            description = item.find("description").text if item.find("description") is not None else ""
            
            # Get categories
            categories = []
            for category in item.findall("category"):
                if category.text:
                    categories.append(category.text)
            
            # Handle namespaces properly for creator
            creator = ""
            creator_elem = item.find(".//{http://purl.org/dc/elements/1.1/}creator")
            if creator_elem is not None and creator_elem.text:
                creator = creator_elem.text
                
            items.append({
                "title": item.find("title").text if item.find("title") is not None else "",
                "link": item.find("link").text if item.find("link") is not None else "",
                "description": description,
                "pub_date": pub_date,
                "formatted_date": formatted_date,
                "categories": categories,
                "creator": creator
            })
        
        return {
            "status": "success",
            "feed_info": feed_info,
            "items": items
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error when trying to parse DepEd RSS feed: {str(e)}"
        }


# Define the search agent with only google_search tool
search_agent = Agent(
    name="search_assistant",
    model="gemini-2.5-flash-preview-04-17",
    description="Assistant that searches the web for general information, weather, and news",
    instruction="""
    You are a helpful assistant specializing in searching the web for:
    - General information on any topic
    - Current weather conditions and forecasts
    - Latest news stories and updates
    
    Always use Google Search to find the most up-to-date and accurate information when answering questions.
    """,
    tools=[google_search]  # Only one built-in tool per agent
)

# Define the hackernews agent with custom tools
hackernews_agent = Agent(
    name="hackernews_agent",
    model="gemini-2.5-flash-preview-04-17",
    description="Agent to get the top hackernews posts and trending github repos",
    instruction="I can get the top hacker news posts and the trending github repos",
    tools=[get_hackernews_posts, get_github_trending_repos]  # These are custom functions, not built-in tools
)

# Define the DepEd RSS feed agent
deped_agent = Agent(
    name="deped_agent",
    model="gemini-2.5-flash-preview-04-17",
    description="Agent that fetches and parses the latest news from the Department of Education (DepEd) RSS feed",
    instruction="""
    You are a helpful assistant specializing in providing the latest news and updates from the Department of Education (DepEd). 
    You can fetch the most recent articles, press releases, memoranda, and other official communications from DepEd.
    
    When users ask about DepEd news, use the get_deped_rss_feed tool to fetch the latest information.
    Be sure to present the information in a clear, well-organized format.
    
    If there's an issue connecting to the RSS feed, let the user know and offer to search for DepEd news using the search_assistant instead.
    """,
    tools=[get_deped_rss_feed]  # Custom function for DepEd RSS feed
)

# Create a coordinator agent that uses agent_tool to access the specialized agents
root_agent = Agent(
    name="information_coordinator",
    model="gemini-2.5-flash-preview-04-17",
    description="I coordinate between retrieving tech news, education news, and performing web searches.",
    instruction="""
    You are a helpful information assistant. You can:
    1. Retrieve the latest tech news from Hacker News and trending GitHub repositories
    2. Search the web for additional information when needed
    3. Fetch the latest news and updates from the Department of Education (DepEd)
    
    Use the appropriate agent tool based on the user's query:
    - Use the hackernews_agent for questions about current tech news and GitHub trends
    - Use the search_assistant for general questions requiring web search
    - Use the deped_agent for questions about Department of Education news, updates, and official communications
    
    If one agent encounters an error, try to use another relevant agent to still provide helpful information.
    For example, if the deped_agent cannot connect to the RSS feed, use the search_assistant to find recent DepEd news.
    """,
    tools=[
        agent_tool.AgentTool(agent=search_agent),
        agent_tool.AgentTool(agent=hackernews_agent),
        agent_tool.AgentTool(agent=deped_agent)
    ]
)