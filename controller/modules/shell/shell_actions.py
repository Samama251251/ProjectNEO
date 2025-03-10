from google import generativeai
from dotenv import load_dotenv
from library.helper_functions import clean_content
import os
import subprocess


#* Configurations
load_dotenv()
generativeai.configure(api_key = os.getenv("GOOGLE_GENAI_API"))

#* Initializing Model
model = generativeai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=os.getenv("OS_SETTINGS")
)

chat = model.start_chat(history=[])

async def shell_actions(prompt):
    output = []
    current_working_directory = os.getcwd()
    print(prompt)
    content = chat.send_message(prompt)
    response = clean_content(content.text)
    print(response)
    commands_list = [cmd['command' or 'cmd'] for cmd in response['commands']]

    for command in commands_list:
        print("\033[1;36mExecuting Command: \033[1;0m" + command)
        
        # Execute the command with the specified working directory
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            cwd=current_working_directory  # Specify the working directory
        )

        # Update the working directory if the command changes it
        if command.startswith("cd "):  # Check if the command changes the directory
            new_dir = command[3:].strip()
            if os.path.isdir(new_dir):
                current_working_directory = os.path.abspath(new_dir)
            else:
                print(f"Error: Directory '{new_dir}' does not exist.")
        
        # Print any errors
        if result.stderr:
            print("Error:")
            print(result.stderr)
            output.append(result.stderr)
        # Print the output
        print("Output:")
        print(result.stdout)
        output.append(result.stdout)
    
    return output

