from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def lti_entry():
    if request.method == 'POST':
        # Mostrar todos los datos recibidos
        data = {k: v for k, v in request.form.items()}
        return render_template_string("""
            <h2>¡Hola desde LTI!</h2>
            <h4>Datos recibidos de Schoology:</h4>
            <pre>{{ data | safe }}</pre>
        """, data=data)
    return "<h2>¡Funciona el endpoint LTI!</h2><p>Esperando POST...</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
