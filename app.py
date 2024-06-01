from flask import Flask, request
import sett
import services
import expert_system

app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    expert_system.menu()
    return 'Bienvenidoooooooooooooo'

@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == sett.token and challenge != None:
            return challenge
        else:
            return 'token incorrecto', 403
    except Exception as e:
        return e,403
    
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']#services.replace_start(message['from'])
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)

        services.administrar_chatbot(text, number, messageId, name)
        return 'enviado'

    except Exception as e:
        return e,403


if __name__ == '__main__':
    config = dotenv_values(".env")
    app.run()
    