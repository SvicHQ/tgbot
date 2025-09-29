from app import logger

def extract_cmd_args(text, commands, prefixes=None):
    """
    Extracts args from given text by removing command & prefixes.
    
    :param text: the text to get args from
    :param commands: list of command names
    :param prefixes: list of command prefixes (default: ["/", "!", "-", "."])
    :return: stripped text after removing command and prefix
    """
    try:
        if prefixes is None:
            prefixes = ["/", "!", "-", "."]
        
        for p in prefixes:
            if text.startswith(p):
                text = text[len(p):]
                break
        
        for c in commands:
            if text.startswith(c):
                text = text[len(c):]
                break
        
        return text.strip()
    except Exception as e:
        logger.error(e)
