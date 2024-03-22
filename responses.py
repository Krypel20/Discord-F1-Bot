def handle_response(message) ->str:
    p_message = message.lower()
    
    if p_message == 'hejka':
        return 'Hejka!'
    
    if p_message == 'f1':
        return 'Jeszcze nic nie wiem'
    
    if p_message == 'f1!help':
        return 'Tutaj będę wyswietlał dostepne komendy'
    
    if p_message.startswith('jebany bot'):
        return 'Morda cwelu okok'