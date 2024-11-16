import speech_recognition as sr
import pyttsx3
import sqlite3

# Inicializar el motor de texto a voz
engine = pyttsx3.init()

# Configuración de la base de datos SQLite
conn = sqlite3.connect('inventario.db')
cursor = conn.cursor()

# Crear la tabla de inventario si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS inventario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT NOT NULL,
    precio_bolivares REAL NOT NULL
)
''')
conn.commit()

# Función para actualizar el tipo de cambio
def actualizar_tipo_cambio(nuevo_cambio):
    global tipo_cambio
    tipo_cambio = nuevo_cambio

# Inicializar el tipo de cambio (manual)
tipo_cambio = 0.02  # Ejemplo: 1 bolívar = 0.02 dólares

# Función para convertir precios a dólares
def convertir_a_dolares(precio_bolivares):
    return precio_bolivares * tipo_cambio

# Reconocimiento de voz
def escuchar_comando():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = r.listen(source)
        try:
            comando = r.recognize_google(audio, language='es-ES')
            print(f"Comando: {comando}")
            return comando.lower()
        except sr.UnknownValueError:
            print("No se pudo entender el comando.")
            return ""
        except sr.RequestError:
            print("Error al conectarse al servicio de reconocimiento de voz.")
            return ""

# Función para responder con voz
def responder(mensaje):
    engine.say(mensaje)
    engine.runAndWait()

# Función principal del asistente
def asistente_virtual():
    while True:
        comando = escuchar_comando()
        if "precio del" in comando:
            producto = comando.replace("precio del ", "").strip()
            cursor.execute('SELECT precio_bolivares FROM inventario WHERE producto=?', (producto,))
            resultado = cursor.fetchone()
            if resultado:
                precio_bolivares = resultado[0]
                precio_dolares = convertir_a_dolares(precio_bolivares)
                respuesta = f"El precio del {producto} es {precio_bolivares} bolívares o {precio_dolares:.2f} dólares."
                responder(respuesta)
            else:
                responder("Producto no encontrado en el inventario.")
        elif "actualizar tipo de cambio a" in comando:
            nuevo_cambio = float(comando.replace("actualizar tipo de cambio a ", "").strip())
            actualizar_tipo_cambio(nuevo_cambio)
            responder(f"Tipo de cambio actualizado a {tipo_cambio} dólares por bolívar.")
        elif "salir" in comando:
            responder("Cerrando asistente virtual.")
            break

# Ejecución del asistente virtual
if __name__ == "__main__":
    asistente_virtual()
