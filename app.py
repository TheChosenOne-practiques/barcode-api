from flask import Flask, request, send_file
from barcode import Code128
from barcode.writer import ImageWriter
import io
import base64
import os
import openpyxl

app = Flask(__name__)

# Crear carpeta
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


# ✅ PANTALLA PRINCIPAL
@app.route("/")
def home():
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    rows = ""
    for row in ws.iter_rows(min_row=2, values_only=True):
        rows += f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>"

    return f"""
    <h2>Generador de código de barras</h2>

    <form action="/barcode">
        <input type="text" name="data" placeholder="Introduce el número" style="padding:10px;">
        <button type="submit" style="padding:10px;">Generar</button>
    </form>

    <br>

    <a href="/download_excel">
        <button style="padding:10px;">Descargar Excel</button>
    </a>

    <h3>Códigos guardados</h3>

    <table border="1" cellpadding="5">
        <tr>
            <th>Nº</th>
            <th>Código</th>
        </tr>
        {rows}
    </table>
    """


# ✅ GENERAR CÓDIGO
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

        filename = f"barcode_{data}.png"
        filepath = f"barcodes/{filename}"

        # Guardar imagen
        with open(filepath, "wb") as f:
            f.write(buffer.getvalue())

        # Guardar en Excel
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        next_row = ws.max_row + 1
        ws[f"A{next_row}"] = next_row - 1
        ws[f"B{next_row}"] = data

        wb.save(excel_path)

        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"""
        <h2>Código generado</h2>

        <img src="data:image/png;base64,{img_base64}"/>

        <br><br>

        <a href="/download_image?name={filename}">
            <button style="padding:10px;">Descargar imagen</button>
        </a>

        <br><br>

        <a href="/">
            <button style="padding:10px;">Volver</button>
        </a>
        """

    except Exception as e:
        return str(e), 500


# ✅ DESCARGAR EXCEL
@app.route("/download_excel")
def download_excel():
    return send_file(excel_path, as_attachment=True)


# ✅ DESCARGAR IMAGEN
@app.route("/download_image")
def download_image():
    name = request.args.get("name")
    path = f"barcodes/{name}"

    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "Archivo no encontrado", 404


if __name__ == "__main__":
    app.run()
