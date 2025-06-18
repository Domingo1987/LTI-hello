from flask import Flask, request, render_template_string, abort
from ims_lti_py.tool_provider import ToolProvider

# Tus credenciales LTI (¡reemplazá por las que pongas en Schoology!)
LTI_CONSUMER_KEY = "test"
LTI_SHARED_SECRET = "test"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def lti_launch():
    if request.method == "POST":
        # Autenticar LTI usando ims-lti-py
        tool_provider = ToolProvider(LTI_CONSUMER_KEY, LTI_SHARED_SECRET, request.form)
        if not tool_provider.is_valid_request(request):
            return abort(403, description="LTI launch inválido o no autenticado.")

        # Si pasó, mostrar datos recibidos
        user_id = request.form.get("user_id", "Desconocido")
        return render_template_string("""
            <h2>¡Hola, autenticación LTI exitosa!</h2>
            <p>Usuario: {{ user_id }}</p>
            <pre>{{ data }}</pre>
        """, user_id=user_id, data=dict(request.form.items()))

    return "<h2>¡Endpoint LTI listo!</h2><p>Debés ingresar desde el LMS.</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
