import json

def history():
    with open('data/history.json', 'r') as f:
        history = json.load(f)

    table = """"""

    show_range = min(50, len(history))
    if not show_range:   # Neu khong co vi pham nao
        return table

    for i in range(1, show_range+1):
        row = history[-i]
        table += """
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1.5px solid #ccc; padding-bottom: 8px; padding-top: 8px; font-size: 16px">
                <div style="width: 33.33%">{}</div>
                <div style="flex: 1">{}</div>
                <img src="{}" alt="Image" style="width: 160px; height: 160px; object-fit: cover" />
            </div>
            """.format(row['name'], row['date'], row['evidence'])

    return table