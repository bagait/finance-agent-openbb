# Finance Agent with OpenBB

This project is an AI agent that can answer financial questions by understanding natural language, translating the query into a command for the [OpenBB Platform](https://openbb.co/), executing it, and summarizing the results.

It demonstrates a powerful "tool-use" pattern where a Large Language Model (LLM) acts as a reasoning engine to call external tools (in this case, the comprehensive OpenBB SDK) to answer questions it couldn't answer on its own.



### Features

-   **Natural Language Understanding**: Ask complex financial questions in plain English.
-   **Tool Translation**: Uses a fast LLM (via Groq) to convert your question into a precise OpenBB Python command.
-   **Live Data Fetching**: Executes the command to fetch real-time or historical financial data.
-   **AI-Powered Summarization**: Another LLM call synthesizes the fetched data into a human-readable answer.

## How It Works

The agent follows a simple three-step process:

1.  **Translate**: The agent takes your query (e.g., "What's the latest news for Apple?") and feeds it to an LLM with a specialized prompt. This prompt instructs the model to act as a financial expert and convert the query into a single, executable line of OpenBB Python code, like `obb.news.company(symbol='AAPL', provider='benzinga').to_json()`.

2.  **Execute**: The agent takes the generated command string and executes it using `eval()`. This calls the OpenBB SDK, which fetches the requested data from financial data providers. The data is returned as a JSON string.
    
    > **Security Note**: Using `eval()` is a potential security risk. This project is for educational purposes and should be run in a controlled environment. Never run code from untrusted sources.

3.  **Summarize**: The agent takes the original query and the retrieved JSON data and sends them to the LLM one more time. A final prompt asks the model to act as a financial analyst and provide a concise answer based on the given data.

This entire process creates a powerful RAG (Retrieval-Augmented Generation) system where the "retrieval" step is a dynamic API call to the world of financial data.

## Installation

1.  **Clone the repository:**

    bash
    git clone https://github.com/bagait/finance-agent-openbb.git
    cd finance-agent-openbb
    

2.  **Create a virtual environment and install dependencies:**

    bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    

3.  **Set up API Keys:**

    You will need two keys:
    -   **OpenBB PAT (Personal Access Token)**: Sign up for free at [my.openbb.co](https://my.openbb.co/app/platform/pat) to get your key.
    -   **Groq API Key**: Sign up at [console.groq.com](https://console.groq.com/keys) for a free, fast LLM API key.

    Create a file named `.env` in the project root and add your keys:

    
    OPENBB_PAT="YOUR_OPENBB_TOKEN_HERE"
    GROQ_API_KEY="YOUR_GROQ_API_KEY_HERE"
    

## Usage

Run the agent from your command line by passing a query in quotes.

**Example 1: Fetching Company News**

bash
python main.py "What is the latest news for Tesla?"


**Example 2: Getting Historical Stock Data**

bash
python main.py "Show me historical prices for Microsoft since the start of 2024"


**Example 3: Finding Analyst Price Targets**

bash
python main.py "What are the recent analyst price targets for Nvidia?"


**Example 4: Comparing Key Metrics**

bash
python main.py "get key metrics for both apple and google for the last year"


## License

This project is licensed under the MIT License. See the LICENSE file for details.
