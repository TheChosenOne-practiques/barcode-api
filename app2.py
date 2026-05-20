from flask import Flask, request
from barcode import Code128
from barcode.writer import ImageWriter
import io

app = Flask(__name__)

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

        return buffer.getvalue(), 200, {"Content-Type": "image/png"}

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run()