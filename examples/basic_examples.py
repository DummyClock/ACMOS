import requests, json, sys, os

#Add the ACMOS Directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Now import the webhook
from auth import WEBHOOK_URL

#Somewhat messy but this is mostly the fully written blocks & fields, without using a package/library

#Used to create nice title blocks for each example section
def title_block(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": "*" + text + "*"}}
#Used to create nice title fields for each example section
def title_field(text):
    return {"type": "mrkdwn", "text": "*" + text + "*"}
#To make my life easier, a function for the multi-select menu options
def menu_item(text, value):
    return {"text": {"type": "plain_text","text": text}, "value": value}
#Used as a dividing line between sections
divider = {"type" : "divider"}

#Used for variable examples
block_type = "section"
section_type = "mrkdwn"
section_text = "Alongside this variable text, for a varible block and section type."
variable_block = {"type" : block_type,"text": {"type": section_type,"text": section_text}}

data = {
    "blocks": [
        title_block("Plain Text 'body' Example"),
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "This is the body text, inside a section."
            }
        },
        divider, title_block("Divider Line & Variable Examples"), variable_block, divider,
        {
            "type": "section",
            "fields": [
                title_field("Fields & Markdown Text Formatting Examples"),
                {
                    "type": "mrkdwn",
                    "text": (
                        "_Italic Text_\n"
                        "~Strikethrough Text~\n"
                        "*Bold Text*\n"
                        "~*_Everything Text_*~\n"
                        "> Blockquote\n"
                        "```\nCode Block\n```\n"
                        "`Inline Code Block`\n"
                    )
                }
            ]
        },
        divider,
        title_block("Image Example"),
        {
            "type": "image",
            "image_url": "https://1000logos.net/wp-content/uploads/2021/04/Chick-fil-A-logo.png",
            "alt_text": "Chickfila Logo" #Narrator Text
        },
        divider,
        title_block("Context Block Example"),
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "This is a context block with some text. Cannot be nested in a field."
                },
                {
                    "type": "image",
                    "image_url": "https://pbs.twimg.com/profile_images/1148729107406041088/emlH0Rv4_400x400.png",
                    "alt_text": "Circle Chickfila Logo"
                }
            ]
        },
        divider,
        title_block("Section with a button"),
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Click Me"
                    },
                    "url": "https://www.google.com"
                }
            ]
        },
        divider,
        {
            "type": "section",
            "text" : title_field("Date Picker Example"),
            "accessory": {
                "type": "datepicker",
                "initial_date": "2023-01-01",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                }
            }
        },
        divider,
        {
            "type": "section",
            "text" : title_field("User Picker Example"),
            "accessory": {
                "type": "users_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a user"
                }
            }
        },
        divider,
        {
            "type": "section",
            "text": title_field("Multi-select Menu Example"),
            "accessory": {
                "type": "multi_static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select items"
                },
                "options": [# Options for ther multi-select menu, 1 for show, rest are function-made
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Item 1"
                        },
                        "value": "item_1"
                    },
                    menu_item("Item 2", "item_2"),
                    menu_item("Item 3", "item_3")
                ]
            }
        }
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
print(response.status_code) #<=200 is good, >=400 is bad
print(response.text) #"ok" if good, or states error/issue
