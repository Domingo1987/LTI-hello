from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def lti_entry():
    if request.method == 'POST':
        user = request.form.get('user_id', 'Desconocido')
        return render_template_string(
            "<h2>¡Hola, LTI!</h2><p>Bienvenido/a, usuario: {{ user }}</p>", user=user)
    return "<h2>¡Funciona el endpoint LTI!</h2><p>Esperando POST...</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
