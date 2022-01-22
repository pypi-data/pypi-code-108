css = [
    {"selector": "table, th, td", "props": [("border", "0")]},
    {
        "selector": "thead th",
        "props": [
            ("padding", "10px 3px"),
            ("border-bottom", "1px solid black"),
            ("text-align", "right"),
        ],
    },
    {"selector": "td", "props": [("padding", "3px")]},
    {"selector": ".row_heading", "props": [("padding-right", "3px")]},
]

css_typ = [
    {"selector": "tr:nth-child(even)", "props": [("background-color", "#eeeeee")]},
    {"selector": "td:nth-child(odd)", "props": [("text-align", "right")]},
    {"selector": "th:nth-child(odd)", "props": [("color", "white")]},
    {
        "selector": "td:nth-child(even)",
        "props": [("text-align", "center"), ("font-size", "0.9em")],
    },
]

css_corr = [
    {"selector": "td, th", "props": [("text-align", "center")]},
    # {"selector": "thead th", "props": [("text-align", "center !important")]},
    {"selector": "tbody th", "props": [("text-align", "right")]},
    {
        "selector": "th.col_heading",
        "props": [("writing-mode", "vertical-rl"), ("transform", "rotateZ(-90deg)")],
    },
]
