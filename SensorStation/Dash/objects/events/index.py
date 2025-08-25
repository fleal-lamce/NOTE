from dash import callback_context


class Events:
    def __init__(self):
        pass

    def clicked(self, key):
        return callback_context.triggered and callback_context.triggered[0]["prop_id"].startswith(key)
    
    