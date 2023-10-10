import os
import requests

urls = [
    "https://sunmanapp.blob.core.windows.net/publicstuff/workplace-app-tariffs-bym.json",
    "https://sunmanapp.blob.core.windows.net/publicstuff/workplace-app-tariffs-elser.json",
    "https://sunmanapp.blob.core.windows.net/publicstuff/workplace-app-tariffs-summary-ada-002.json"



]

output_dir = "../output"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for url in urls:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Extract the filename from the URL and join it with the output directory
    filename = os.path.join(output_dir, os.path.basename(url))

    # Write the content to the file
    with open(filename, 'wb') as file:
        file.write(response.content)

    print(f"Downloaded {url} to {filename}")

print("All downloads completed!")
