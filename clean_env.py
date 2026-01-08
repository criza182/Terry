import os

file_path = ".env"
try:
    with open(file_path, "rb") as f:
        content = f.read()
    
    # Check for UTF-8 BOM
    if content.startswith(b'\xef\xbb\xbf'):
        print("UTF-8 BOM detected. Removing...")
        new_content = content[3:]
        with open(file_path, "wb") as f:
            f.write(new_content)
        print("BOM removed successfully.")
    else:
        print("No UTF-8 BOM detected.")
        
    # Also check for UTF-16 BOM if necessary, but unlikely for .env
    
except Exception as e:
    print(f"Error: {e}")
