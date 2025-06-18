from flask import Flask, request, render_template_string, abort
from lti import ToolProvider

app = Flask(__name__)

LTI_CONSUMER_KEY = "test"
LTI_SHARED_SECRET = "test"

@app.route("/", methods=["GET", "POST"])
def lti_entry():
    if request.method == "POST":
        tool_provider = ToolProvider.from_request(
            request.method,
            request.url,
            request.form,
            consumers={LTI_CONSUMER_KEY: LTI_SHARED_SECRET}
        )

        if not tool_provider.is_valid_request():
            return abort(403, description="LTI launch inválido o no autenticado.")

        user_id = tool_provider.user_id or "Desconocido"
        roles = tool_provider.roles or "No especificado"
        return render_template_string("""
            <h2>¡Autenticación LTI exitosa!</h2>
            <p>Usuario: {{ user_id }}</p>
            <p>Rol: {{ roles }}</p>
            <h4>Todos los datos recibidos:</h4>
            <pre>{{ data }}</pre>
        """, user_id=user_id, roles=roles, data=tool_provider.launch_params)
    else:
        return "<h2>¡Funciona el endpoint LTI!</h2><p>Esperando POST...</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
