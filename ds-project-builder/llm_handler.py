# llm_handler.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


print(f"DEBUG: Loaded Google API Key starts with: {os.getenv('GOOGLE_API_KEY')[:8] if os.getenv('GOOGLE_API_KEY') else 'None'}")


# Configure the Gemini API client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_app_with_llm(brief: str) -> dict:
    """
    Generates application files (HTML, README) using Gemini.
    Returns a dictionary like {"index.html": "...", "README.md": "..."}
    """
    print("🤖 Sending brief to Gemini to generate code...")

    # This is the instruction we give to the AI.
    # The format with [START ...] and [END ...] is crucial so we can easily parse the output.
    prompt = f"""
    You are an expert, minimalist web developer. You create simple, single-file web applications using only HTML and vanilla JavaScript. You do not use external libraries unless explicitly asked.

    **Task:** Based on the following brief, generate a complete and runnable `index.html` file and a professional `README.md` file.

    **Brief:** "{brief}"

    **Instructions:**
    1.  Generate the content for `index.html`.
    2.  Generate the content for `README.md`.
    3.  Respond with ONLY the raw code for the files in the specified format below, and nothing else. Do not add any explanation or conversational text outside of the file blocks.

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
        content = response.text

        # Parse the response to extract the code for each file
        html_code = content.split("[START index.html]")[1].split("[END index.html]")[0].strip()
        readme_code = content.split("[START README.md]")[1].split("[END README.md]")[0].strip()
        
        print("✅ Code generated successfully!")
        
        return {
            "index.html": html_code,
            "README.md": readme_code
        }
    except Exception as e:
        print(f"❌ Error generating code with LLM: {e}")
        return None