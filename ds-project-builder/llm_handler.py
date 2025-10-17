# llm_handler.py
import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
import base64 # <-- Make sure base64 is imported


load_dotenv()


print(f"DEBUG: Loaded Google API Key starts with: {os.getenv('GOOGLE_API_KEY')[:8] if os.getenv('GOOGLE_API_KEY') else 'None'}")


# Configure the Gemini API client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')


def parse_llm_response(content: str) -> dict | None:
    """
    A robust parser to extract multiple files from an LLM's response
    using regular expressions.
    """
    try:
        print(f"📄 Raw LLM Response (first 500 chars):\n{content[:500]}...")

        # Use regex to find all file blocks, handling potential extra text
        # re.DOTALL makes '.' match newlines, which is crucial here
        html_match = re.search(r"\[START index.html\](.*?)\[END index.html\]", content, re.DOTALL)
        readme_match = re.search(r"\[START README.md\](.*?)\[END README.md\]", content, re.DOTALL)

        if not html_match or not readme_match:
            print(f"❌ ERROR: Expected markers not found in LLM response!\nFull response:\n{content}")
            return None

        html_code = html_match.group(1).strip()
        readme_code = readme_match.group(1).strip()

        return {
            "index.html": html_code,
            "README.md": readme_code
        }

    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}")
        return None


def generate_app_with_llm(brief: str, attachments: list | None = None) -> dict:
    """
    Generates application files (HTML, README) using Gemini,
    now with intelligent handling for different attachment types (data vs. assets).
    """
    print("🤖 Sending brief to Gemini to generate code...")

    attachment_context = ""
    if attachments:
        print(f"📄 Processing {len(attachments)} attachment(s)...")
        for attachment in attachments:
            try:
                header, encoded_data = attachment['url'].split(',', 1)
                mime_type = header.split(';')[0].split(':')[1]

                # --- THIS IS THE NEW LOGIC ---
                # If it's an image, we tell the LLM to use the data URI directly.
                if mime_type.startswith('image/'):
                    attachment_context += f"\n--- Asset Attachment: {attachment['name']} ---\n"
                    attachment_context += f"Use this full Data URI as a source URL (e.g., in an <img> src attribute):\n"
                    attachment_context += f"```\n{attachment['url']}\n```\n"
                # Otherwise, we assume it's data and decode it.
                else:
                    decoded_content = base64.b64decode(encoded_data).decode('utf-8')
                    attachment_context += f"\n--- Data Attachment: {attachment['name']} ---\n"
                    attachment_context += f"```\n{decoded_content[:2000]}\n```\n" # Limit to first 2000 chars

            except Exception as e:
                print(f"⚠️  Could not process attachment {attachment['name']}: {e}")
    
    # The prompt is updated with clearer instructions
    prompt = f"""
    You are an expert, minimalist web developer. You create simple, single-file web applications using only HTML and vanilla JavaScript.

    **Task:** Based on the following brief and any provided attachments, generate a complete and runnable `index.html` file and a professional `README.md` file.

    **Brief:** "{brief}"
    {attachment_context if attachment_context else "**Attachments:** None provided."}
    **Instructions:**
    1.  If "Data Attachments" are provided, your JavaScript code MUST use the data from them to fulfill the brief.
    2.  If "Asset Attachments" are provided, your HTML/CSS code MUST use the full Data URI as a source for elements like images. Do NOT try to decode the asset content.
    3.  Generate the content for `index.html`.
    4.  Generate the content for `README.md`.
    
    **CRITICAL INSTRUCTION:** You MUST respond with ONLY the raw code for the files in the specified format below. Do not add any explanation or conversational text outside of the file blocks. Your response must contain the `[START ...]` and `[END ...]` markers.

    [START index.html]
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Generated App</title>
    </head>
    <body>
        </body>
    </html>
    [END index.html]
    [START README.md]
    # Project Title
    
    A brief summary of what this project does.
    
    ## How to Use
    
    Instructions on how to use the web page.
    
    ## Code Explanation
    
    A short explanation of the HTML/JavaScript code.
    
    ## License
    
    This project is licensed under the MIT License.
    [END README.md]
    """

    try:
        response = model.generate_content(prompt)
        # --- THIS IS THE UPGRADED PART ---
        parsed_files = parse_llm_response(response.text)
        if parsed_files:
            print("✅ Code generated and parsed successfully!")
            return parsed_files
        else:
            raise ValueError("Failed to parse LLM response.")
            
    except Exception as e:
        print(f"❌ Error generating code with LLM: {e}")
        return None

def revise_app_with_llm(new_brief: str, existing_html: str, attachments: list | None = None) -> dict | None:
    """
    Revises an existing HTML file using Gemini, now with intelligent
    handling for attachments during the revision process.
    """
    print("🤖 Sending existing code and new brief to Gemini for revision...")

    attachment_context = ""
    if attachments:
        print(f"📄 Processing {len(attachments)} attachment(s) for revision...")
        for attachment in attachments:
            try:
                header, encoded_data = attachment['url'].split(',', 1)
                mime_type = header.split(';')[0].split(':')[1]

                if mime_type.startswith('image/'):
                    attachment_context += f"\n--- New Asset Attachment: {attachment['name']} ---\n"
                    attachment_context += f"Incorporate this new asset. Use its full Data URI as a source URL:\n"
                    attachment_context += f"```\n{attachment['url']}\n```\n"
                else:
                    decoded_content = base64.b64decode(encoded_data).decode('utf-8')
                    attachment_context += f"\n--- New Data Attachment: {attachment['name']} ---\n"
                    attachment_context += f"Incorporate this new data into the application logic:\n"
                    attachment_context += f"```\n{decoded_content[:2000]}\n```\n"

            except Exception as e:
                print(f"⚠️  Could not process attachment {attachment['name']}: {e}")

    prompt = f"""
    You are an expert web developer specializing in updating existing code.
    Your task is to modify the provided HTML file based on a new request, potentially incorporating new data or assets from attachments.

    **Instructions:**
    1.  Carefully analyze the "EXISTING index.html".
    2.  Implement the changes described in the "NEW BRIEF".
    3.  If new attachments are provided, integrate them as instructed (use data in JS, use asset URIs in HTML/CSS).
    4.  Generate an updated `README.md` that reflects the new functionality.
    
    **CRITICAL INSTRUCTION:** You MUST respond with ONLY the raw code for the updated files in the specified format below. Do not add any explanation or conversational text outside of the file blocks. Your response must contain the `[START ...]` and `[END ...]` markers.

    ---
    **EXISTING index.html:**
    ```html
    {existing_html}
    ```
    ---
    **NEW BRIEF:**
    "{new_brief}"
    ---
    {attachment_context if attachment_context else "**New Attachments:** None provided."}
    ---

    [START index.html]
    <!DOCTYPE html>
    ... your updated html code ...
    </html>
    [END index.html]
    [START README.md]
    # Updated Project Title
    ... your updated readme content ...
    [END README.md]
    """

    try:
        response = model.generate_content(prompt)
        # --- THIS IS THE UPGRADED PART ---
        parsed_files = parse_llm_response(response.text)
        if parsed_files:
            print("✅ Code revised and parsed successfully!")
            return parsed_files
        else:
            raise ValueError("Failed to parse LLM response.")

    except Exception as e:
        print(f"❌ Error revising code with LLM: {e}")
        return None