#!/usr/local/bin/pypy3.10
import subprocess
import json
import logging
import time

# Configure logging to output to a file in /opt/encoder directory
log_file = '/opt/encoder/adblock.log'
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to clear the contents of the file after a delay
def clear_sidecar_file():
    time.sleep(10)  # Wait for 10 seconds
    with open('/opt/mark/sidecar.txt', 'w') as f:
        f.truncate(0)  # Clear the file contents

# Function to check the next clip and execute the command if the name contains "break"
def check_and_execute_command():
    try:
        # Execute the curl command to get the token
        user = "USUARIO"
        password = "SENHA"
        token_command = f"curl -s -X POST http://127.0.0.1:8787/auth/login/ -H 'Content-Type: application/json' -d '{{\"username\": \"{user}\", \"password\": \"{password}\"}}'"
        
        # Run the command and capture output
        token_output = subprocess.check_output(token_command, shell=True)

        # Debug: Log the raw token response
        logging.info(f"Token Response: {token_output.decode('utf-8')}")

        # Parse the token from the curl output
        token_data = json.loads(token_output.decode('utf-8'))

        # Extract the token from the nested user data
        token = token_data.get("user", {}).get("token")

        if not token:
            logging.error("Error retrieving token: No token found in the response")
            return

        # Log the token (optional)
        logging.info(f"Token: {token}")

        # Execute the curl command to get the current media info
        current_command = f"curl -s -X GET http://127.0.0.1:8787/api/control/1/media/current -H 'Content-Type: application/json' -H 'Authorization: Bearer {token}'"
        current_output = subprocess.check_output(current_command, shell=True)

        # Parse the returned JSON
        current_data = json.loads(current_output)

        # Extract the necessary data (duration and source)
        media = current_data.get("media")
        if not media:
            logging.error("Media data is not available in the response")
            return

        clip_name = media.get("source")
        duration = media.get("duration")

        # Check if the file name contains "break"
        if "break" in clip_name:
            # Build the command with dynamic duration
            command = f'adbreak -d {duration} -s /opt/mark/sidecar.txt'
            # Log the command to the log file
            logging.info(f"Executing command: {command}")
            # Execute the command using subprocess
            subprocess.run(command, shell=True)
            print(f"Command executed for clip '{clip_name}' with 'break' in the name and dynamic duration {duration}.")
        else:
            print(f"The next clip '{clip_name}' does not contain 'break' in the name.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Curl command failed: {e.output.decode('utf-8')}")
    except json.JSONDecodeError:
        logging.error("Failed to parse JSON response")
    except Exception as e:
        logging.error(f"Error processing the request: {str(e)}")

# Call the function to check and execute the command
check_and_execute_command()

# Call the function to clear the sidecar file after 10 seconds
clear_sidecar_file()
