# Retail Inventory AI Assistant

A full-stack, AI-powered Retail Inventory Assistant using a React frontend, a FastAPI/LangGraph backend, and a Model Context Protocol (MCP) server. It includes advanced capabilities like **Demand Forecasting**, **Price Optimization**, and **Knowledge Base Search (RAG)**.

## Project Structure

- **`frontend/`**: A React application (built with Vite) providing a premium, dynamic chat UI.
- **`backend/`**: A FastAPI service that uses LangGraph to orchestrate an AI agent. It seamlessly integrates with the MCP server to dynamically invoke your custom inventory tools.
- **`mcp_server/`**: The core MCP server implementation (`server.py`) and database helper methods (`db.py`).
- **`data/`**: Contains mock inventory data (`inventory.csv`), the SQLite database (`inventory.db`), and the database initialization script (`init_db.py`).

---

## 1. Initial Setup

Before running anything, make sure you have initialized the mock inventory database. From the root of the project:
```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install root dependencies
pip install -r requirements.txt

# Seed the database
python data/init_db.py

# Initialize the Knowledge Base (RAG)
python data/init_rag.py
```

---

## 2. Running the AI Backend (FastAPI + LangGraph)

The backend exposes a `/chat` endpoint and automatically spins up the MCP server to give the AI access to the retail inventory data.

1. **Configure Environment Variables**:
   Navigate to the `backend/` directory and configure your API Keys:
   ```bash
   cp backend/.env.example backend/.env
   # Open backend/.env and add your OPENAI_API_KEY
   # Also add a secure, random string for APP_API_KEY
   ```

2. **Install Backend Dependencies**:
   Ensure your virtual environment is still activated from the root directory:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start the Backend Server**:
   From the `backend/` directory, start the FastAPI server:
   ```bash
   cd backend
   python main.py
   ```
   *The server will run on `http://localhost:8000`.*

---

## 3. Running the Chat UI (React)

The frontend is a sleek Vite-powered React application.

1. **Install Dependencies**:
   Open a **new terminal tab**, navigate to the `frontend/` directory, and install the Node modules:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment Variables**:
   The frontend must send an API key to the backend. Create a `.env.local` file:
   ```bash
   # Add your matching VITE_APP_API_KEY to this file
   echo "VITE_APP_API_KEY=your_secure_api_key_here" > .env.local
   ```

3. **Start the Development Server**:
   ```bash
   npm run dev
   ```

Open your browser to `http://localhost:5173` to interact with your AI Inventory Assistant!

---

## Advanced: Testing the MCP Server Directly

If you want to manually test the MCP Server tools (`inventory.get_stock`, `inventory.product_search`, `forecast_demand`, `optimize_price`) independently from the AI chatbot, you can use the official MCP Inspector from the root directory:
```bash
npx @modelcontextprotocol/inspector .venv/bin/python mcp_server/server.py
```
