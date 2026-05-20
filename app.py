from flask import Flask, request, send_file
from barcode import Code128
from barcode.writer import ImageWriter
import io
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
    ws["A1"] = "Nº"
    ws["B1"] = "Código"
    wb.save(excel_path)


# ✅ FORMULARIO PRINCIPAL
@app.route("/")
def home():
    return '''
    <h2>Generador de código de barras</h2>
    <form action="/barcode">
        <input type="text" name="data" placeholder="Introduce el número" style="padding:10px;">
        <button type="submit" style="padding:10px;">Generar</button>
    </form>
    '''


# ✅ GENERAR + DESCARGAR + MOSTRAR
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

        # Guardar archivo
        with open(filepath, "wb") as f:
            f.write(buffer.getvalue())

        # Guardar en Excel
        wb = openpyxl.load_workbook(excel_path)
        ws = wb.active

        next_row = ws.max_row + 1
        ws[f"A{next_row}"] = next_row - 1
        ws[f"B{next_row}"] = data

        wb.save(excel_path)

        # ✅ CLAVE: devolver imagen directamente
        return send_file(
            filepath,
            mimetype="image/png",
            as_attachment=True,     # 🔥 descarga automática
            download_name=filename  # nombre archivo
        )

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run()
