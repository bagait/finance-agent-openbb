import os
import json
import argparse
import warnings
from dotenv import load_dotenv
from groq import Groq
from openbb import obb

# Suppress pandas future warnings from OpenBB
warnings.simplefilter(action='ignore', category=FutureWarning)

class FinanceAgent:
    """An AI agent that uses OpenBB to answer financial questions."""

    def __init__(self, groq_api_key: str, openbb_pat: str):
        """
        Initializes the FinanceAgent.

        Args:
            groq_api_key (str): Your Groq API key.
            openbb_pat (str): Your OpenBB Personal Access Token.
        """
        if not groq_api_key or not openbb_pat:
            raise ValueError("GROQ_API_KEY and OPENBB_PAT must be set.")
        
        self.groq_client = Groq(api_key=groq_api_key)
        obb.account.login(pat=openbb_pat)
        print("Successfully logged into OpenBB.")

        self.model = "llama3-70b-8192"

    def _get_openbb_command(self, query: str) -> str:
        """
        Uses an LLM to translate a natural language query into an OpenBB command.
        """
        print(f"\n> Translating query to OpenBB command: '{query}'")
        system_prompt = """
        You are an expert financial analyst AI. Your task is to translate a user's natural language query into a single, executable Python command using the OpenBB library (`obb`).

        Guidelines:
        1.  Only use functions available in the OpenBB SDK.
        2.  The final output must be a single line of executable Python code. For example: `obb.equity.price.historical(symbol='AAPL', start_date='2023-01-01', provider='fmp').to_df().to_json()`
        3.  If the command returns a data structure (like a DataFrame or a Pydantic model), you MUST append `.to_df().to_json(orient='records', date_format='iso')` or `.to_json()` to convert the output to a JSON string. This is crucial for the system to parse the data.
        4.  Do not generate any text other than the command itself. No explanations, no markdown, just the code.

        Examples:
        - User Query: "What's the latest news for Microsoft?"
        - Command: `obb.news.company(provider='benzinga', symbol='MSFT', limit=5).to_json()`

        - User Query: "Get historical stock prices for NVDA from the start of 2024"
        - Command: `obb.equity.price.historical(symbol='NVDA', start_date='2024-01-01', provider='fmp').to_df().to_json(orient='records', date_format='iso')`

        - User Query: "Show me the latest analyst estimates for GOOGL"
        - Command: `obb.equity.estimates.price_target(symbol='GOOGL', provider='fmp').to_df().to_json(orient='records', date_format='iso')`
        """
        
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            model=self.model,
            temperature=0,
        )
        command = chat_completion.choices[0].message.content.strip()
        # Sometimes the model might wrap the command in markdown
        if command.startswith('`python\n'):
            command = command[8:-4].strip()
        if command.startswith('`'):
             command = command.strip('`')

        print(f"< Generated Command: {command}")
        return command

    def _execute_command(self, command: str) -> str:
        """
        Executes the generated OpenBB command and returns the data.
        WARNING: Uses eval(), which is a security risk. Do not run untrusted commands.
        """
        print("\n> Executing command...")
        try:
            # SECURITY WARNING: eval() can execute arbitrary code.
            # This is for demonstration purposes in a controlled environment.
            # In a production system, use a safer method to execute commands.
            result = eval(command)
            # The result should already be a JSON string based on the prompt.
            # If it's not, we try to convert it.
            if not isinstance(result, str):
                 result = json.dumps(result, indent=2)
            print("< Command executed successfully.")
            return result
        except Exception as e:
            print(f"< Error executing command: {e}")
            return json.dumps({"error": str(e)})

    def _summarize_result(self, query: str, data: str) -> str:
        """
        Uses an LLM to summarize the data and answer the user's query.
        """
        print("\n> Summarizing data...")

        # Truncate data if it's too long to avoid exceeding context limits
        max_data_length = 15000
        if len(data) > max_data_length:
            data = data[:max_data_length] + "... [data truncated]"
        
        system_prompt = """
        You are an expert financial analyst AI. You will be given a user's question and the corresponding data retrieved from the OpenBB financial platform.
        Your task is to provide a clear, concise, and helpful answer to the user's question based *only* on the provided data.
        If the data contains an error, acknowledge the error and explain what might have gone wrong.
        Format your answer in well-structured markdown.
        """

        user_content = f"Original Question: {query}\n\nRetrieved Data (in JSON format):\n{data}"

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            model=self.model,
        )
        summary = chat_completion.choices[0].message.content
        print("< Summary generated.")
        return summary

    def run(self, query: str):
        """
        Runs the full agent pipeline for a given query.
        """
        command = self._get_openbb_command(query)
        data = self._execute_command(command)
        summary = self._summarize_result(query, data)

        print("\n" + "-"*50)
        print("Final Answer:")
        print("-"*50)
        print(summary)
        print("-"*50 + "\n")

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Finance Agent using OpenBB and Groq")
    parser.add_argument("query", type=str, help="Your financial question in natural language.")
    args = parser.parse_args()

    try:
        agent = FinanceAgent(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            openbb_pat=os.getenv("OPENBB_PAT")
        )
        agent.run(args.query)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please make sure you have a .env file with GROQ_API_KEY and OPENBB_PAT set.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
