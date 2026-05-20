from flask import Flask, request
from barcode import Code128
from barcode.writer import ImageWriter
import io
import base64
import os
import openpyxl

app = Flask(__name__)

# Crear carpeta si no existe
if not os.path.exists("barcodes"):
    os.makedirs("barcodes")

excel_path = "barcodes/registros.xlsx"

# Crear Excel si no existe
if not os.path.exists(excel_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Códigos"

    ws["A1"] = "Nº"
    ws["B1"] = "Código"

    wb.save(excel_path)


# ✅ Pantalla principal
@app.route("/")
def home():
    return '''
    <h2>Generador de código de barras</h2>
    <form action="/barcode">
        <input type="text" name="data" placeholder="Introduce el número" style="padding:10px;">
        <button type="submit" style="padding:10px;">Generar</button>
    </form>
    '''


# ✅ Generar código
@app.route("/barcode")
def barcode():
    data = request.args.get("data")

    if not data:
        return "Falta ?data=123456", 400

    try:
        # Crear barcode en memoria
        buffer = io.BytesIO()
        codigo = Code128(data, writer=ImageWriter())
        codigo.write(buffer)
        buffer.seek(0)

        # ✅ Guardar imagen en carpeta
        filename = f"barcodes/barcode_{data}.png"
        with open(filename, "wb") as f:
            f.write(buffer.getvalue())

        # ✅ Guardar en Excel
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        next_row = ws.max_row + 1
        ws[f"A{next_row}"] = next_row - 1
        ws[f"B{next_row}"] = data

        wb.save(excel_path)

        # ✅ Convertir imagen a base64 para mostrar
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f'''
        <h2>Código generado</h2>

        <img src="data:image/png;base64,{img_base64}">

        <p>Guardado como: {filename}</p>

        <br><br>

        <a href="/">
            <button style="padding:10px;">Volver</button>
        </a>
        '''

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run()
