def handle_response(message) ->str:
    p_message = message.lower()
    
    if p_message == 'hejka':
        return 'Hejka!'
    
    if p_message == 'f1' or p_message == 'results' or p_message == 'standings':
        return 'Użyj ukośnika przed komendą tumanie. O w ten sposób -> /f1'
    
    if p_message.startswith('jebany bot'):
        return 'Morda cwelu okok'
    
    if p_message.startswith('@F1 RACE WEEK'):
        return '??'
    
    if p_message.startswith('znak zapytania'):
        return 'Zjeb'