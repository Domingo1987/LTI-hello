from flask import Flask, request, render_template_string, redirect, jsonify
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configuración LTI desde variables de entorno
LTI_KEY = os.environ.get('LTI_KEY', 'schoology_test_key_123')
LTI_SECRET = os.environ.get('LTI_SECRET', 'schoology_test_secret_456')

print(f"🔧 Configuración LTI:")
print(f"   Consumer Key: {LTI_KEY}")
print(f"   Secret: {'*' * len(LTI_SECRET)}")
print(f"   Debug: {app.debug}")

def validate_oauth_signature(request_data, url, method="POST"):
    """Valida la firma OAuth de la petición LTI"""
    
    # Extraer parámetros
    params = dict(request_data)
    oauth_signature = params.pop('oauth_signature', [''])[0]
    
    # Crear string base para firma
    normalized_params = []
    for key, values in sorted(params.items()):
        for value in values:
            normalized_params.append(f"{key}={urllib.parse.quote(str(value), safe='')}")
    
    param_string = "&".join(normalized_params)
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    
    # Crear firma
    signing_key = f"{urllib.parse.quote(LTI_SECRET, safe='')}&"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    
    return signature == oauth_signature

@app.route('/lti', methods=['GET', 'POST'])
def lti_launch():
    """Endpoint principal para el lanzamiento LTI"""
    
    if request.method == 'GET':
        # Manejar peticiones GET (para depuración)
        return """
        <h2>🔤 Herramienta LTI - Contador de Caracteres</h2>
        <p><strong>⚠️ Esta herramienta debe ser lanzada desde Schoology</strong></p>
        <p>Si ves este mensaje, significa que:</p>
        <ul>
            <li>✅ La URL es correcta</li>
            <li>⚠️ Pero debe ser accedida mediante POST desde el LMS</li>
        </ul>
        <hr>
        <h3>🔧 Para probar manualmente:</h3>
        <form method="POST">
            <input type="hidden" name="user_id" value="test_user">
            <input type="hidden" name="context_id" value="test_context">
            <input type="hidden" name="resource_link_id" value="test_resource">
            <button type="submit">🚀 Probar Herramienta</button>
        </form>
        """
    
    if request.method == 'POST':
        # Validar firma OAuth (en producción siempre validar)
        # is_valid = validate_oauth_signature(request.form, request.url)
        # if not is_valid:
        #     return "Firma OAuth inválida", 403
        
        # Extraer información del usuario y contexto
        user_id = request.form.get('user_id', 'unknown')
        context_id = request.form.get('context_id', 'unknown')
        resource_link_id = request.form.get('resource_link_id', 'unknown')
        
        # Crear formulario para entrada de texto
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Contador de Caracteres</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                textarea { width: 100%; height: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #005a8b; }
                .result { margin-top: 20px; padding: 15px; background: #e8f4f8; border-radius: 4px; }
                .info { color: #666; font-size: 12px; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔤 Contador de Caracteres</h2>
                <div class="info">
                    Usuario: {{ user_id }} | Contexto: {{ context_id }}
                </div>
                
                <form method="POST" action="/analyze">
                    <input type="hidden" name="user_id" value="{{ user_id }}">
                    <input type="hidden" name="context_id" value="{{ context_id }}">
                    <input type="hidden" name="resource_link_id" value="{{ resource_link_id }}">
                    
                    <label for="texto">Introduce el texto a analizar:</label><br><br>
                    <textarea name="texto" id="texto" placeholder="Escribe aquí tu texto..."></textarea><br><br>
                    
                    <button type="submit">📊 Analizar Texto</button>
                </form>
                
                <div id="live-count" style="margin-top: 10px; color: #666;">
                    Caracteres: <span id="count">0</span>
                </div>
            </div>
            
            <script>
                // Contador en tiempo real
                document.getElementById('texto').addEventListener('input', function() {
                    const count = this.value.length;
                    document.getElementById('count').textContent = count;
                });
            </script>
        </body>
        </html>
        """
        
        return render_template_string(html_template, 
                                    user_id=user_id, 
                                    context_id=context_id,
                                    resource_link_id=resource_link_id)
    
    else:
        return """
        <h2>Herramienta LTI - Contador de Caracteres</h2>
        <p>Esta herramienta debe ser lanzada desde un LMS compatible con LTI 1.1</p>
        <p>Configure la URL de lanzamiento como: <code>https://tu-servidor.com/lti</code></p>
        """

@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analiza el texto enviado y muestra resultados"""
    
    texto = request.form.get('texto', '')
    user_id = request.form.get('user_id', 'unknown')
    context_id = request.form.get('context_id', 'unknown')
    
    # Análisis del texto
    num_caracteres = len(texto)
    num_palabras = len(texto.split()) if texto.strip() else 0
    num_lineas = len(texto.split('\n'))
    
    # Template de resultados
    result_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resultados del Análisis</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .result-box { background: white; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007cba; }
            .text-preview { background: #f9f9f9; padding: 10px; border-radius: 4px; max-height: 150px; overflow-y: auto; margin: 10px 0; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: white; padding: 15px; border-radius: 4px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat-number { font-size: 24px; font-weight: bold; color: #007cba; }
            .stat-label { color: #666; font-size: 14px; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            button:hover { background: #005a8b; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 Resultados del Análisis</h2>
            
            <div class="result-box">
                <h3>Texto Analizado:</h3>
                <div class="text-preview">{{ texto[:200] }}{% if texto|length > 200 %}...{% endif %}</div>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ num_caracteres }}</div>
                    <div class="stat-label">Caracteres</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ num_palabras }}</div>
                    <div class="stat-label">Palabras</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ num_lineas }}</div>
                    <div class="stat-label">Líneas</div>
                </div>
            </div>
            
            <div class="result-box">
                <h3>🎯 Resultado Principal</h3>
                <p style="font-size: 18px;"><strong>El texto tiene {{ num_caracteres }} caracteres.</strong></p>
            </div>
            
            <a href="javascript:history.back()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none;">
                ← Analizar Otro Texto
            </a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(result_template, 
                                texto=texto,
                                num_caracteres=num_caracteres,
                                num_palabras=num_palabras,
                                num_lineas=num_lineas,
                                user_id=user_id,
                                context_id=context_id)

@app.route('/config.xml')
def lti_config():
    """Configuración XML para LTI"""
    # Detectar la URL base desde la petición
    base_url = request.url_root.rstrip('/')
    
    config_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<cartridge_basiclti_link xmlns="http://www.imsglobal.org/xsd/imslticc_v1p0"
    xmlns:blti="http://www.imsglobal.org/xsd/imsbasiclti_v1p0"
    xmlns:lticm="http://www.imsglobal.org/xsd/imslticm_v1p0"
    xmlns:lticp="http://www.imsglobal.org/xsd/imslticp_v1p0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imslticc_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd
    http://www.imsglobal.org/xsd/imsbasiclti_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0p1.xsd
    http://www.imsglobal.org/xsd/imslticm_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd
    http://www.imsglobal.org/xsd/imslticp_v1p0 http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd">
    <blti:title>Contador de Caracteres</blti:title>
    <blti:description>Herramienta para contar caracteres, palabras y líneas en un texto</blti:description>
    <blti:launch_url>{base_url}/lti</blti:launch_url>
    <blti:secure_launch_url>{base_url}/lti</blti:secure_launch_url>
    <blti:icon>{base_url}/static/icon.png</blti:icon>
    <blti:secure_icon>{base_url}/static/icon.png</blti:secure_icon>
    <blti:extensions platform="schoology.com">
        <lticm:property name="domain">{base_url.replace('https://', '').replace('http://', '')}</lticm:property>
        <lticm:property name="tool_id">contador_caracteres</lticm:property>
        <lticm:property name="privacy_level">public</lticm:property>
    </blti:extensions>
</cartridge_basiclti_link>"""
    
    return config_xml, 200, {'Content-Type': 'application/xml'}

@app.route('/health')
def health_check():
    """Endpoint para verificar que la aplicación funciona"""
    return jsonify({
        'status': 'ok',
        'lti_key': LTI_KEY,
        'endpoints': {
            'launch': '/lti',
            'config': '/config.xml',
            'health': '/health'
        }
    })

@app.route('/')
def index():
    """Página de inicio con información de la herramienta"""
    base_url = request.url_root.rstrip('/')
    
    info_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Herramienta LTI - Contador de Caracteres</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .container {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
            .endpoint {{ background: white; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007cba; }}
            .code {{ background: #f8f8f8; padding: 10px; border-radius: 4px; font-family: monospace; }}
            .success {{ color: #28a745; }}
            .info {{ color: #17a2b8; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔤 Herramienta LTI - Contador de Caracteres</h1>
            <p class="success">✅ Aplicación funcionando correctamente</p>
            
            <div class="endpoint">
                <h3>📋 Configuración para Schoology</h3>
                <p><strong>URL de lanzamiento:</strong></p>
                <div class="code">{base_url}/lti</div>
                
                <p><strong>Consumer Key:</strong></p>
                <div class="code">{LTI_KEY}</div>
                
                <p><strong>Shared Secret:</strong></p>
                <div class="code">{LTI_SECRET}</div>
            </div>
            
            <div class="endpoint">
                <h3>🔧 Endpoints Disponibles</h3>
                <ul>
                    <li><a href="/lti">🚀 /lti</a> - Punto de lanzamiento LTI</li>
                    <li><a href="/config.xml">📄 /config.xml</a> - Configuración XML</li>
                    <li><a href="/health">💚 /health</a> - Estado de la aplicación</li>
                </ul>
            </div>
            
            <div class="endpoint">
                <h3>🔗 URL de ngrok</h3>
                <p class="info">Usa esta URL completa en Schoology: <strong>{base_url}/lti</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return info_html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Iniciando servidor Flask en puerto {port}")
    print(f"🔧 Debug: {debug}")
    print(f"💡 Accede a http://localhost:{port} para ver la configuración")
    
    # Para desarrollo con ngrok
    app.run(debug=debug, host='0.0.0.0', port=port)
    
    # Para producción, usa un servidor WSGI como Gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app