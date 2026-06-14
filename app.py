from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Mengambil data dari form HTML
        kategori = request.form.get('kategori')
        laporan = request.form.get('laporan')
        
        # Langsung kirim data ke halaman response.html
        return render_template('response.html', kategori=kategori, laporan=laporan)
    
    # Menampilkan halaman utama form.html
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)