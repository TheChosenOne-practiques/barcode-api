from flask import Flask, request
from barcode import Code128
from barcode.writer import ImageWriter
import io
import base64

app = Flask(__name__)

# ✅ Pantalla principal (formulario)
@app.route("/")
def home():
    return '''
    <h2>Generador de código de barras</h2>
    <form action="/barcode">
        <input type="text" name="data" placeholder="Introduce el número" style="padding:10px;">
        <button type="submit" style="padding:10px;">Generar</button>
    </form>
    '''


# ✅ Generar código de barras
@app.route("/barcode")
def barcode():
    data = request.args.get("data")

    if not data:
        return "Falta ?data=123456", 400

    try:
        buffer = io.BytesIO()

        codigo = Code128(data, writer=ImageWriter())
        codigo.write(buffer)
        buffer.seek(0)

        # Convertir imagen a base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f'''
        <h2>Código generado</h2>

        <img src="data:image/png;base64,{img_base64}"/>

        <br><br>

        <a href="/">
            <button style="padding:10px;">Volver</button>
        </a>
        '''

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run()
