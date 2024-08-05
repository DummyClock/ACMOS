import os, sys

#Add the ACMOS Directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Now import the webhook
#from auth import WEBHOOK_URL
WEBHOOK_URL = os.environ["WEBHOOK_URL"]


def runBlock(block):
    """
    Runs a singular block

    Args:
        block : a 'json' block to run
    
    Returns:
        int: Status code of the URL request.
            - 200-299: OK
            - 404: Not Found
            - 400: Error
    """
    import json, requests
    data = {
        "blocks": [block]
    }
    headers ={"Content-Type": "application/json"}
    response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
    return response.status_code

def runBlocks(blocks):
    """
    Runs a list of blocks

    Args:
        blocks (list): a list of 'json' formatted blocks
    
    Returns:
        int: Status code of the URL request.
            - 200-299: OK
            - 404: Not Found
            - 400: Error
    """
    import json, requests
    data = {
        "blocks": blocks
    }
    headers ={"Content-Type": "application/json"}
    response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
    return response.status_code

def markdownBlock(text, returns=True):
    """
    Creates or sends a simple block using markdown.

    Args:
        text (str): Text to be displayed/sent.
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "section","text": {"type": "mrkdwn","text": text}}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def markdownField(text):
    """
    Creates a simple field using markdown.

    Args:
        text (str): Text to be displayed/sent.

    Returns:
        dict: The 'json' formatted field to be sent to Slack.
    """
    return {"type": "mrkdwn", "text": text}

def textBlock(text, returns=True):
    """
    Creates or sends a simple plain text block

    Args:
        text (str): Text to be displayed/sent.
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "section","text": {"type": "plain_text","text": text}}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def textField(text):
    """
    Creates a simple block for plain text

    Args:
        text (str): Text to be displayed/sent.

    Returns:
        dict: The 'json' formatted field to be sent to Slack.
    """
    return {"type": "plain_text","text": text}

def headerBlock(text, returns=True):
    """
    Creates or sends a simple plain text block as a header

    Args:
        text (str): Text to be displayed/sent.
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "header","text": {"type": "plain_text","text": text}}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def imageBlock(url, alt_text="", returns=True):
    """
    Creates or sends an image block; This block displays an image

    Args:
        url (str): URL of the image.
        alt_text (str): Alternative Text for the image; Description or name used for accessibility
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "image", "image_url": url, "alt_text": alt_text}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def dividerBlock(returns=True):
    """
    Creates or sends a divider block; This block creates a dividing line

    Args:
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "divider"}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def fieldBlock(fields, returns=True):
    """
    Creates or sends a field block; A field block can contain multiple markdown or plaintext fields blocks within for one big block.

    Args:
        fields (list): A List of markdown/plaintext field blocks
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {"type": "section","fields": fields}
    if(returns == False):
        return runBlock(block)
    else:
        return block

def buttonBlock(text, value, id, returns=True):
    """
    Creates or sends a button block

    Args:
        text (str): Text within the button object
        value (str): Unique identifier for the object
        id (str): Another unique identifier mainly used for event listeners/action
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": text,
                },
                "value": value,
                "action_id": id
            }
        ]
    }
    if(returns == False):
        return runBlock(block)
    else:
        return block

def datePicker(text, id, placeholder="Select a Date", returns=True):
    """
    Creates or sends a date picker block

    Args:
        text (str): Text being a prompt for the interactive menu
        id (str): Unique identifier mainly used for event listeners/action
        placeholder (str): Placeholder text seen in the displayed & interactive portion of the button
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {
        "type": "section",
        "text": markdownField(text),
        "accessory": {
            "type": "datepicker",
            "initial_date": "2023-01-01",
            "placeholder": {
                "type": "plain_text",
                "text": placeholder
            },
            "action_id": id
        }
    }
    if(returns == False):
        return runBlock(block)
    else:
        return block

def userPicker(text, id, placeholder="Select a User", returns=True):
    """
    Creates or sends a block thats picks a user

    Args:
        text (str): Text being a prompt for the interactive menu
        id (str): Unique identifier mainly used for event listeners/action
        placeholder (str): Placeholder text seen in the displayed & interactive portion of the button
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    block = {
        "type": "section",
        "text": markdownField(text),
        "accessory": {
            "type": "users_select",
            "placeholder": {
                "type": "plain_text",
                "text": placeholder
            },
            "action_id": id
        }
    }
    if(returns == False):
        return runBlock(block)
    else:
        return block

def multiselectItem(text, id):
    """
    Creates an item/option block for a Multi-Select Menu

    Args:
        text (str): Text being a prompt for the interactive menu
        id (str): Unique identifier 

    Returns:
        dict: The 'json' formatted block to be used in the Multi-Select Menu
    """
    return {"text": {"type": "plain_text","text": text},"value": id}

def multiselectMenu(text, placeholder, options, id, returns=True):
    """
    Creates or sends a Multi-Select Menu Block

    Args:
        text (str): Text being a prompt for the interactive menu
        placeholder (str): Placeholder text seen in the displayed & interactive portion of the button
        options (list): A list containing many lists which are pairs of an item and it's id
        id (str): Unique identifier mainly used for event listeners/action
        returns (bool): If True (default), return the block; if False, send it.

    Returns:
        dict or int: Either the 'json' formatted block to be sent to Slack (if returns is True) or the status code of the webhook (if returns is False).
    """
    itemList = []
    for item in options:
        itemList.append(multiselectItem(item[0],item[1]))
    block = {
        "type": "section",
        "text": markdownField(text),
        "accessory": {
            "type": "multi_static_select",
            "placeholder": {
                "type": "plain_text",
                "text": placeholder
            },
            "options": itemList,
            "action_id": id
        }
    }
    if(returns == False):
        return runBlock(block)
    else:
        return block
