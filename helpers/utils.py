# helpers/utils.py
def save_to_file(content, filename="generated_content.txt"):
    """
    Save content to a text file.

    Parameters:
        content (str): The content to save.
        filename (str): The name of the file.

    Returns:
        str: Confirmation message with the file path.
    """
    try:
        with open(filename, "w") as file:
            file.write(content)
        return f"Content successfully saved to {filename}"
    except Exception as e:
        return f"Error saving content: {e}"
