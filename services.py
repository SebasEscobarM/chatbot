import requests
import sett
import json
import time
from expert_system import *

expert_system = SymptomsExpert()
preguntas=[ "¿No podía sentir ningún sentimiento positivo?",
            "¿Se me hizo difícil tomar la iniciativa para hacer cosas?",
            "¿He sentido que no había nada que me ilusionara?",
	        "¿Me sentí triste y deprimido?",
            "¿No me pude entusiasmar por nada?",
            "¿Sentí que valía muy poco como persona?",
            "¿Sentí que la vida no tenía ningún sentido?",

	        "¿Me di cuenta que tenía la boca seca?",
	        "¿Se me hizo difícil respirar?",
	        "¿Sentí que mis manos temblaban?",
            "¿Estaba preocupado por situaciones en las cuales podía tener pánico o en las que podría hacer el ridículo?",
	        "¿Sentí que estaba a punto del pánico?",
            "¿Sentí los latidos de mi corazón a pesar de no haber hecho ningún esfuerzo físico?",
	        "¿Tuve miedo sin razón?",

	        "¿Me ha costado mucho descargar la tensión?",
	        "¿Reaccioné exageradamente en ciertas situaciones?",
	        "¿He sentido que estaba gastando una gran cantidad de energía?",
            "¿Me he sentido inquieto?",
	        "¿Se me hizo difícil relajarme?",
            "¿No toleré nada que no me permitiera continuar con lo que estaba haciendo?",
	        "¿He tendido a sentirme enfadado con facilidad?"]


respuestas=[]
preguntas_hechas=0

preguntas.reverse()

def obtener_Mensaje_whatsapp(message):
    if 'type' not in message :
        text = 'mensaje no reconocido'
        return text

    typeMessage = message['type']
    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    else:
        text = 'mensaje no procesado'
    
    
    return text

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("se envia ", data)
        response = requests.post(whatsapp_url, 
                                 headers=headers, 
                                 data=data)
        
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return e,403
    
def text_Message(number,text):
    data = json.dumps(
            {
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "body": text
                }
            }
    )
    return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {
                    "id": sedd + "_btn_" + str(i+1),
                    "title": option
                }
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

def listReply_Message(number, options, body, footer, sedd,messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str( i+1),
                "title": option,
                "description": ""
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": [
                        {
                            "title": "Secciones",
                            "rows": rows
                        }
                    ]
                }
            }
        }
    )
    return data

def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data

def administrar_chatbot(text,number, messageId, name):
    text = text.lower() #mensaje que se recibió del usuario
    list = []

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    #Anidado de mensajes a responder según la respuesta del usuario
    if "hola" in text:
        body = "*¡Hola!* 👋\nBienvenido al sistema de primeros auxilios psicológicos para estudiantes de la Universidad ICESI.\n¿Cómo podemos ayudarte?"
        footer = "Bienestar universitario ICESI"
        options = ["Número de atención 📱", "Test rápido ✅"]

        mainMenu = buttonReply_Message(number, options, body, footer, "sed1", messageId)

        list.append(mainMenu)

    elif "número de atención" in text:
        data = text_Message(number,"*Para contactar telefónicamente* 📱\n   Ana Cristina Marín F.\n   Directora de Desarrollo Humano y Promoción de la Salud\n   572-5552334 Ext. 8350\nSi necesitas algo más no dudes en contactarnos.\n*Bienestar Universitario ICESI*")
        list.append(data)
    
    elif  "test rápido" in text:
        body = "*Prepárate para comenzar el test!*\nPrimero te preguntaremos algo de tus datos escenciales, y luego tendrás varias preguntas en las que deberás de elegir de la lista de opciones la que consideres con total sinceridad.\nLos datos que ingreses aquí serán tratados con total confidencialidad."
        footer = "Bienestar universitario ICESI"
        options = ["Comenzar test 📄"]

        mainMenu = buttonReply_Message(number, options, body, footer, "sed2", messageId)

        list.append(mainMenu)
    
    elif "comenzar test" in text:
        data = text_Message(number, "*Datos personales*\nEscribe por favor tu codigo estudiantil en formato A00XXXX")
        list.append(data)

    elif "a00" in text:
        #Respuesta a codigo
        data = text_Message(number, "*¡Gracias!*\nAhora si, comencemos con las preguntas")

        #Primera pregunta
        body = preguntas.pop()
        footer = "Bienestar Universitario ICESI"
        options = ["Si ✅", "No ❌"]
        

        listReply = listReply_Message(number, options, body, footer, "sed3",messageId)

        list.append(data)
        list.append(listReply)
    
    elif "si" in text:
        respuestas.append("yes")

        if len(preguntas)==0:
            data = text_Message(number, "*Terminaste*\nEspera mientras damos tu resultado... 📄")
            list.append(data)
            #Se pasa todo al sistema experto
            expert_system.reset
            expert_system.declare(Symptom(positive_feeling=respuestas[0],initiative=respuestas[1],illusion=respuestas[2],depressed=respuestas[3],nothing_enthusiastic=respuestas[4],
                worth_little=respuestas[5],no_sense=respuestas[6],dry_mouth=respuestas[7],difficulty_breathing = respuestas[8], hands_trembled = respuestas[9], panic_ridicule=respuestas[10],
                panic=respuestas[11],heartbeat_physicalexertion=respuestas[12],fear_no_reason=respuestas[13],unloading_tension=respuestas[14],exaggerated_reaction=respuestas[15],expending_great_energy=respuestas[16],
                restlessness=respuestas[17],difficult_relax=respuestas[18],no_tolerate_continue=respuestas[19],easily_angered=respuestas[20]))
            expert_system.run()

            r=bn(expert_system)
            data2=text_Message(number,"*Respuesta*\nNivel de depresión: "+r[0]+"\nNivel de ansiedad: "+r[1]+"\nNivel de estres: "+r[2])

            list.append(data2)

            body = "*Te recomendamos agendar cita con uno de nuestros psicólogos* 📱\n   Ana Cristina Marín F.\n   Directora de Desarrollo Humano y Promoción de la Salud\n   572-5552334 Ext. 8350\nSi necesitas algo más no dudes en contactarnos."
            footer = "Bienestar universitario ICESI"
            options = ["Menú principal ✅"]

            last = buttonReply_Message(number, options, body, footer, "sed1", messageId)

            list.append(last)
        else:
            body = preguntas.pop()
            footer = "Bienestar Universitario ICESI"
            options = ["Si ✅", "No ❌"]

            listReply = listReply_Message(number, options, body, footer, "sed3",messageId)
            list.append(listReply)
        
    elif "no" in text:
        respuestas.append("no")

        if len(preguntas)==0:
            data = text_Message(number, "*Terminaste*\nEspera mientras damos tu resultado... 📄")
            list.append(data)
            #Se pasa todo al sistema experto
            expert_system.reset
            expert_system.declare(Symptom(positive_feeling=respuestas[0],initiative=respuestas[1],illusion=respuestas[2],depressed=respuestas[3],nothing_enthusiastic=respuestas[4],
                worth_little=respuestas[5],no_sense=respuestas[6],dry_mouth=respuestas[7],difficulty_breathing = respuestas[8], hands_trembled = respuestas[9], panic_ridicule=respuestas[10],
                panic=respuestas[11],heartbeat_physicalexertion=respuestas[12],fear_no_reason=respuestas[13],unloading_tension=respuestas[14],exaggerated_reaction=respuestas[15],expending_great_energy=respuestas[16],
                restlessness=respuestas[17],difficult_relax=respuestas[18],no_tolerate_continue=respuestas[19],easily_angered=respuestas[20]))
            expert_system.run()

            r=bn(expert_system)
            data2=text_Message(number,"*Respuesta*\nNivel de depresión: "+r[0]+"\nNivel de ansiedad: "+r[1]+"\nNivel de estres: "+r[2])
            list.append(data2)


            body = "*Te recomendamos agendar cita con uno de nuestros psicólogos* 📱\n   Ana Cristina Marín F.\n   Directora de Desarrollo Humano y Promoción de la Salud\n   572-5552334 Ext. 8350\nSi necesitas algo más no dudes en contactarnos."
            footer = "Bienestar universitario ICESI"
            options = ["Menú principal ✅"]

            last = buttonReply_Message(number, options, body, footer, "sed1", messageId)

            list.append(last)

        else:
            body = preguntas.pop()
            footer = "Bienestar Universitario ICESI"
            options = ["Si ✅", "No ❌"]

            listReply = listReply_Message(number, options, body, footer, "sed3",messageId)
            list.append(listReply)

    elif "menú principal" in text:
            data2=text_Message(number,"Hola, necesito ayuda psicológica")
            list.append(data2)
            
    else:
        data = text_Message(number,"Lo siento, no entendí lo que dijiste")
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)
    
"""""
#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
        """
