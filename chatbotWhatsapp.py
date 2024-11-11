from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import openai
import os
from openai.error import RateLimitError
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

# Configuración de la API de OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

def call_endpoint(messages):
    # Mensaje del sistema para ChatGPT
    chatgpt_messages_list = [
        {"role": "system", "content": "Hazte pasar por mi, miguel angel sanchez peñuñuri"},
    ]
    chatgpt_response = chatgpt_messages_list + messages

    # Intentos de reintento en caso de RateLimitError
    for intento in range(5):
        try:
            response = openai.ChatCompletion.create(
                temperature=0.2,
                messages=chatgpt_response,
                model="gpt-3.5-turbo",
            )
            assistant_message = response.choices[0].message.content
            return assistant_message
        except RateLimitError:
            print("Límite de tasa alcanzado, esperando antes de reintentar...")
            time.sleep(10 * (intento + 1))  # Incrementa el tiempo de espera con cada intento
        except Exception as e:
            print(f"Ocurrió un error: {e}")
            return "Lo siento, hubo un problema al procesar tu mensaje."
    return "Límite de intentos alcanzado, intenta nuevamente más tarde."

def iniciar_sesion_whatsapp():
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir=C:\\Users\\Ryzen\\AppData\\Local\\Google\\Chrome\\User Data\\Default')  # Ruta a tu perfil de usuario de Chrome
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 720)
    driver.set_window_position(0, 0)
    driver.implicitly_wait(10)
    driver.get("https://web.whatsapp.com/")
    return driver

# Iniciar sesión en WhatsApp Web
driver = iniciar_sesion_whatsapp()

# Bucle principal para leer y responder mensajes
while True:
    try:
        # Verificar si la ventana de Chrome sigue abierta
        driver.title  # Intenta acceder a la propiedad 'title' para verificar que la ventana está abierta
        
        # Esperar hasta encontrar un mensaje no leído
        new_message = driver.find_element(By.XPATH, '//*[@id="pane-side"]/descendant::span[contains(@aria-label,"unread")]')
        new_message.click()

        # Obtener el último mensaje del chat
        last_messages = driver.find_elements(By.XPATH, '//*[@id="main"]/descendant::div[@role="row"]')
        last_message = last_messages[-1]
        time.sleep(3)
        last_message_text = last_message.find_element(By.XPATH, './/div/div/div[1]/div[1]/div[1]/div/div[1]/div/span[1]/span').text    
        print(f'Mensaje del usuario: {last_message_text}')

        # Preparar el mensaje para enviar a la API de OpenAI
        message_list = [{'role': 'user', 'content': last_message_text}]
        print('Enviando mensaje al servicio de lenguaje')
        
        # Llamada a la API de OpenAI
        api_message = call_endpoint(message_list)

        # Enviar la respuesta en WhatsApp
        message_element = driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div[1]')
        message_element.send_keys(f'{api_message}{Keys.ENTER}')
        message_element.send_keys(Keys.ESCAPE)

    except NoSuchWindowException:
        print("Ventana de Chrome cerrada, reiniciando el navegador...")
        driver = iniciar_sesion_whatsapp()  # Reiniciar el navegador

    except WebDriverException as e:
        print(f"Error del WebDriver: {e}")
        time.sleep(5)  # Esperar antes de reintentar

    except Exception as e:
        print(f"Ocurrió un error en el bucle principal: {e}")
        time.sleep(5)  # Espera antes de intentar nuevamente para evitar bloqueos
