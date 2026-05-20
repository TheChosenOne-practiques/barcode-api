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


# ✅ PANTALLA PRINCIPAL
@app.route("/")
def home():
    return '''
    <h2>Generador de código de barras</h2>

    <input type="text" id="codigo" placeholder="Introduce el número" style="padding:10px;">
    <button onclick="generar()" style="padding:10px;">Generar</button>

    <script>
        function generar() {
            let valor = document.getElementById("codigo").value;

            if (!valor) {
                alert("Introduce un número");
                return;
            }

            // ✅ Descargar automáticamente
            const link = document.createElement("a");
            link.href = "/download?data=" + valor;
            link.download = "barcode_" + valor + ".png";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // ✅ Abrir imagen en nueva pestaña (URL limpia)
            window.open("/barcode?data=" + valor, "_blank");
        }
    </script>
    '''


# ✅ GENERA IMAGEN (para mostrar en navegador)
@app.route("/barcode")
def barcode():
    data = request.args.get("data")

    if not data:
        return "Falta ?data=123456", 400

    buffer = io.BytesIO()
    codigo = Code128(data, writer=ImageWriter())
    codigo.write(buffer)
    buffer.seek(0)

    filename = f"barcode_{data}.png"
    filepath = f"barcodes/{filename}"

    with open(filepath, "wb") as f:
        f.write(buffer.getvalue())

    # guardar en excel
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    next_row = ws.max_row + 1
    ws[f"A{next_row}"] = next_row - 1
    ws[f"B{next_row}"] = data
    wb.save(excel_path)

    # ✅ mostrar imagen en navegador (NO descarga)
    return send_file(filepath, mimetype="image/png")


# ✅ DESCARGA
@app.route("/download")
def download():
    data = request.args.get("data")

    if not data:
        return "Falta data", 400

    filename = f"barcode_{data}.png"
    filepath = f"barcodes/{filename}"

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    app.run()
