import os
from flask import Flask, request, jsonify
from PIL import Image
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/analizar', methods=['POST'])
def analizar_inspeccion():
    try:
        if 'scan_file' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo en la petición'}), 400
        
        file = request.files['scan_file']
        temp_path = '/tmp/inspeccion_temp.jpg'
        file.save(temp_path)
        
        img = Image.open(temp_path)
        
        # Usamos el modelo estándar actual
        model = genai.GenerativeModel('gemini-3.8-flash')
        
        prompt = "Analiza esta hoja de inspección manuscrita de camarón HLSO. Extrae toda la información de la cabecera (Exportador, Lugar, Fecha, Presentación, Orden) y todas las filas de la tabla de muestreo (Talla, Lote, Fecha Prod, Pesos Brutos, Pesos Netos, Unidades/Lb, Uniformidad, Factor, Defectos y Temperatura). Devuelve EXCLUSIVAMENTE un objeto JSON válido, sin bloques de código markdown, con la estructura exacta: {\"cabecera\": {...}, \"muestras\": [...]}"
        
        response = model.generate_content([img, prompt])
        raw_text = response.text.strip()
        
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        import json
        json_data = json.loads(raw_text.strip())
        
        return jsonify({'success': True, 'data': json_data})
        
    except Exception as e:
        # Esto capturará cualquier error interno y te dirá exactamente qué falló en Python
        return jsonify({'success': False, 'error': 'Excepción interna en Python: ' . str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
