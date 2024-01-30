import tiktoken
from typing import List, Dict

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def prune_conversation_to_token_limit(conversation: List[Dict], token_limit: int, encoding_name: str) -> list:
    """Prunes a conversation to a token limit by taking the latest messages in a conversation only.\n
    Counting messages and tokens is done from the very last message of the conversation, working backwards

    Args:
        conversation (List[Dict]): [{"role": str, "content": str}, ...]
        token_limit (int): Depends on your model context window length
        encoding_name (str): depends on how the model encodes tokens

    Returns:
        list: pruned conversation list of message objects
    """
    # Create an empty list to add to
    pruned_conversation = []
    token_count = 0

    # Loop through the conversation
    for item in reversed(conversation):
        content = item['content']
        token_count += num_tokens_from_string(content, encoding_name)

        if token_count > token_limit:
            break
        pruned_conversation += [item]

    return pruned_conversation[::-1]

def parse_conversation_to_string(conversation: list) -> str:
    """Parses message objects in a conversation list into a string to be fed as a prompt template to the LLM endpoint

    Args:
        conversation (list): [{"role": str, "content": str}, ...]

    Returns:
        str: prompt template string
    """
    # Create an empty string to add to
    full_string = ""

    # Loop through the conversation
    for item in conversation:
        # Add the role
        full_string += f"<|im_start|>{item['role']}\n"

        # Add the content
        if isinstance(item['content'], list):
            for content in item['content']:
                full_string += f">>> {content}"
        else:
            full_string += f">>> {item['content']}"

        # Add the end token
        full_string += "<|im_end|>\n"

    return full_string

def parse_string_to_conversation(full_string: str) -> list:
    """Parses a string into a list of message objects in a conversation and returns one conversation list

    Args:
        full_string (str): prompt template string

    Returns:
        list: conversation list of message objects
    """
    # Split the string into lines
    lines = full_string.strip().split('\n')

    parsed_list = []
    current_role = None
    current_content = []

    for line in lines:
        # Check if the line indicates a role
        if line.startswith("<|im_start|>"):
            # Save the previous message if there was one
            if current_role and current_content:
                for item in current_content:
                    parsed_list.append({"role": current_role, "content": item})
                current_content = []
            current_role = line.replace("<|im_start|>", "").strip()
        elif line.startswith(">>>"):
            # Strip the leading '>>>' and add the content
            current_content.append(line[3:].strip().replace("<|im_end|>", ""))
        else:
            # This handles the 'system' role and other non-standard lines
            current_role = line.lower()
            current_content = []

    # Add the last message if there is one
    if current_role and current_content:
        parsed_list.append({"role": current_role, "content": " ".join(current_content)})

    return parsed_list

def parse_response_into_objects(response: str) -> list:
    """Parses a response string into a list of message objects in a conversation and returns one conversation list

    Args:
        response (str): LLM response string

    Returns:
        list: list of message objects that represents the list of message objects a model will reply to the user
    """
    return_list = []
    s = response.split('>>>')[1:]  # split by '>>>' and exclude the first empty string
    s = [item.strip() for item in s]  # remove leading and trailing whitespaces

    for message in s:
      return_list.append({"role": "{assistant}", "content": message})

    return return_list