import random

def handle_response(message) ->str: # stupid, uncensored bot responses to user messages
    p_message = message.lower()
    
    if p_message == 'hejka':
        return 'Hejka!'
    
    if p_message == 'f1' or p_message == 'results' or p_message == 'standings':
        return 'Użyj ukośnika przed komendą tumanie. O w ten sposób -> /f1'
    
    if p_message == '/f1' or p_message == '/results' or p_message == '/standings':
        return 'Brawo kretynie'
    
    if p_message == 'info':
        return 'wpisz /f1 a nie info'
    
    if p_message.startswith('?'):
        return 'Brawokolego znak zapytania napiszę bo jestem taki głupi'
    
    if p_message.startswith('jebany bot') or p_message.startswith('<@1218957474552483933> morda'):
        return 'Morda okok'
    
    if p_message.startswith('<@1218957474552483933>') or p_message.startswith('<@&1224670972561330177>'):
        return '??'
    
    if p_message.startswith('aha'):
        return f'# aha{random.randint(1, 100)}'
    
    if p_message.startswith('przeproś'):
        return f'przepraszam że jestem cwelem :clown:'