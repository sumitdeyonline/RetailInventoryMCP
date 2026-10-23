import sys
import os
# Add the project root to sys.path so we can import mcp_server.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
import mcp_server.db as db

# Initialize FastMCP server
mcp = FastMCP("RetailInventory")

# Initialize InMemoryVectorStore for RAG
try:
    dump_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'vector_store.json')
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    if os.path.exists(dump_path):
        vector_store = InMemoryVectorStore.load(dump_path, embeddings)
    else:
        vector_store = None
except Exception as e:
    vector_store = None
    print(f"Warning: Could not initialize InMemoryVectorStore. RAG queries may fail. {e}")


@mcp.tool()
def get_stock(product_id: str) -> str:
    """
    Retrieve stock information for a specific product using its ID.
    
    Args:
        product_id: The unique identifier of the product (e.g., P1001).
        
    Returns:
        A string describing the current stock level and price, or an error message if not found.
    """
    product = db.get_stock_by_id(product_id)
    if product:
        return f"Product '{product['name']}' (ID: {product['id']}) has {product['stock_quantity']} units in stock. Price: ${product['price']:.2f}."
    else:
        return f"Product with ID '{product_id}' not found."

@mcp.tool()
def product_search(query: str) -> str:
    """
    Search for products by name or category.
    
    Args:
        query: The search term to match against product names or categories.
        
    Returns:
        A string listing matching products with their stock and prices.
    """
    results = db.search_products(query)
    
    if not results:
        return f"No products found matching '{query}'."
    
    response_lines = [f"Found {len(results)} matching product(s):"]
    for p in results:
        response_lines.append(
            f"- {p['name']} (ID: {p['id']}, Category: {p['category']}) "
            f"| Stock: {p['stock_quantity']} | Price: ${p['price']:.2f}"
        )
    
    return "\n".join(response_lines)

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Search unstructured documents like product catalogs, store policies, and operating procedures.
    
    Args:
        query: The natural language search query.
        
    Returns:
        A string containing relevant context snippets from the knowledge base.
    """
    if not vector_store:
        return "Knowledge base is currently unavailable."
        
    try:
        results = vector_store.similarity_search(query, k=3)
        if not results:
            return f"No relevant documents found for '{query}'."
            
        response_lines = [f"Found {len(results)} relevant documents:"]
        for i, doc in enumerate(results):
            source = doc.metadata.get("source", "Unknown")
            # Get just the filename instead of the full path
            filename = os.path.basename(source)
            response_lines.append(f"\n--- Document {i+1} (Source: {filename}) ---")
            response_lines.append(doc.page_content)
            
        return "\n".join(response_lines)
    except Exception as e:
        return f"Error accessing knowledge base: {str(e)}"

@mcp.tool()
def forecast_demand(product_id: str) -> str:
    """
    Forecast the 30-day demand for a specific product.
    
    Args:
        product_id: The unique identifier of the product (e.g., P1001).
        
    Returns:
        A string containing the forecasted demand and trend.
    """
    product = db.get_stock_by_id(product_id)
    if not product:
        return f"Product with ID '{product_id}' not found."
    
    # Forecast = sales_last_30d * seasonality_index
    forecast = int(product['sales_last_30d'] * product['seasonality_index'])
    
    trend = "increasing" if product['seasonality_index'] > 1.0 else "decreasing" if product['seasonality_index'] < 1.0 else "stable"
    
    return (
        f"Demand Forecast for '{product['name']}':\n"
        f"- Historical 30-day Sales: {product['sales_last_30d']} units\n"
        f"- Seasonality Trend: {trend.capitalize()} (Index: {product['seasonality_index']})\n"
        f"- Forecasted Next 30-day Demand: {forecast} units."
    )

@mcp.tool()
def optimize_price(product_id: str) -> str:
    """
    Optimize the pricing strategy for a specific product based on inventory levels and forecasted demand.
    
    Args:
        product_id: The unique identifier of the product (e.g., P1001).
        
    Returns:
        A string containing the pricing recommendation and reasoning.
    """
    product = db.get_stock_by_id(product_id)
    if not product:
        return f"Product with ID '{product_id}' not found."
        
    forecast = int(product['sales_last_30d'] * product['seasonality_index'])
    stock = product['stock_quantity']
    current_price = product['price']
    competitor_price = product['competitor_price_avg']
    cost = product['cost_price']
    
    recommendation = ""
    reasoning = ""
    ideal_price = current_price
    
    if stock > forecast * 2:
        # Heavily overstocked
        ideal_price = max(cost * 1.1, competitor_price * 0.9)
        recommendation = "DISCOUNT (Clearance)"
        reasoning = f"Heavily overstocked ({stock} units vs {forecast} forecast). Recommend dropping price below competitor average to clear inventory, but staying above cost."
    elif stock > forecast:
        # Overstocked
        ideal_price = max(cost * 1.2, competitor_price * 0.95)
        recommendation = "DISCOUNT (Mild)"
        reasoning = f"Overstocked ({stock} units vs {forecast} forecast). Recommend slight discount to stimulate demand."
    elif stock < forecast * 0.5:
        # Heavily understocked
        ideal_price = competitor_price * 1.1
        recommendation = "MARKUP (Premium)"
        reasoning = f"Heavily understocked ({stock} units vs {forecast} forecast). High risk of stockout. Recommend pricing above market average to maximize margin."
    elif stock < forecast:
        # Understocked
        ideal_price = competitor_price * 1.05
        recommendation = "MARKUP (Mild)"
        reasoning = f"Understocked ({stock} units vs {forecast} forecast). Recommend slight price increase towards market average."
    else:
        # Balanced
        ideal_price = current_price
        recommendation = "HOLD"
        reasoning = f"Inventory is balanced ({stock} units vs {forecast} forecast). Current pricing strategy is optimal."

    return (
        f"Pricing Optimization for '{product['name']}':\n"
        f"- Current Price: ${current_price:.2f} | Cost: ${cost:.2f} | Competitor Avg: ${competitor_price:.2f}\n"
        f"- Recommendation: {recommendation}\n"
        f"- Suggested Price: ${ideal_price:.2f}\n"
        f"- Reasoning: {reasoning}"
    )


if __name__ == "__main__":
    # Start the FastMCP server with stdio transport
    mcp.run(transport='stdio')
