from flask import Flask, request, render_template_string
from openai import OpenAI
import re

app = Flask(__name__)

# Configuración del cliente de OpenAI
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

# Lista simple de palabras clave relacionadas con perros
PALABRAS_CLAVE = [
    "perro", "perros", "raza", "razas", "canino", "caninos", "adiestramiento", 
    "adiestrar", "ladrar", "pasear", "mascota", "peludo", "cachorro", 
    "cachorros", "alimentación", "cuidados", "veterinario"
]

def es_pregunta_de_perros(pregunta):
    pregunta = pregunta.lower()
    return any(palabra in pregunta for palabra in PALABRAS_CLAVE)

@app.route('/', methods=['GET', 'POST'])
def index():
    response = None
    error = None

    if request.method == 'POST':
        user_input = request.form.get('question', '').strip()
        if user_input:
            if not es_pregunta_de_perros(user_input):
                response = (
                    "Lo siento, solo puedo responder preguntas relacionadas con perros. "
                    "Por favor, intenta con una pregunta sobre razas, cuidados, alimentación, entrenamiento u otros temas caninos."
                )
            else:
                try:
                    print("Enviando solicitud a la API...")
                    chat = client.chat.completions.create(
                        model="deepseek/deepseek-r1:free",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Eres un asistente experto en perros. Solo puedes responder preguntas "
                                    "sobre perros: razas, cuidados, entrenamiento, salud, alimentación, etc. "
                                    "Si la pregunta no es sobre perros, recházala amablemente."
                                )
                            },
                            {"role": "user", "content": user_input}
                        ],
                        max_tokens=300,
                        timeout=10  # importante
                    )
                    response = chat.choices[0].message.content
                except Exception as e:
                    error = f"Error al conectar con la API: {str(e)}"
                    print("Error:", error)
        else:
            error = "Por favor, escribe una pregunta."
            print("Error:", error)

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="es-mx">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ai el pepe</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; padding: 0; background-color: #f4f4f9; }
                h1 { color: #333; }
                form { margin-bottom: 20px; }
                input[type="text"] { width: 300px; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
                button { padding: 10px 20px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background-color: #0056b3; }
                .response, .error { margin-top: 20px; padding: 15px; border-radius: 5px; }
                .response { background-color: #e8f5e9; border: 1px solid #c8e6c9; color: #2e7d32; }
                .error { background-color: #ffebee; border: 1px solid #ffcdd2; color: #c62828; }
            </style>
        </head>
        <body>
            <h1>Haz una pregunta</h1>
            <form method="POST">
                <input type="text" name="question" placeholder="Escribe tu pregunta aquí">
                <button type="submit">Enviar</button>
            </form>

            {% if response %}
                <div class="response">
                    <h2>Respuesta:</h2>
                    <p>{{ response }}</p>
                </div>
            {% endif %}

            {% if error %}
                <div class="error">
                    <p>{{ error }}</p>
                </div>
            {% endif %}
        </body>
        </html>
    ''', response=response, error=error)

if __name__ == '__main__':
    app.run(debug=True)
