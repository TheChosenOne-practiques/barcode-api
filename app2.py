from flask import Flask, request, send_file
from barcode import Code128
from barcode.writer import ImageWriter
import io

app = Flask(__name__)

@app.route("/barcode")
def barcode():
    data = request.args.get("data")

    if not data:
        return "Falta data", 400

    buffer = io.BytesIO()
    codigo = Code128(data, writer=ImageWriter())
    codigo.write(buffer)
    buffer.seek(0)

    return buffer.getvalue(), 200, {"Content-Type": "image/png"}
