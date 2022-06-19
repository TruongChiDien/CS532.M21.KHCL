import json

def members():
    with open('data/member.json', 'r') as f:
        members = json.load(f)

    table = """"""

    for member in members:
        table += """<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #ccc; padding-bottom: 8px; padding-top: 8px; font-size: 16px">
                        <div style="width: 33.33%">{}</div>
                        <div style="flex: 1">{}</div>
                        <div style="width: max-content">{}</div>
                    </div>
                    """.format(member["name"], member["birth"], member["gender"])

    return table
