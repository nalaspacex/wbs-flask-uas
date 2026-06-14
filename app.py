from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__, template_folder='templates')

# Menggunakan kunci base64 statis yang valid untuk Fernet (32-bytes)
KUNCI_RAHASIA = b'HogwartsSecretKeyForCryptoUAS2026Base64='
fernet = Fernet(KUNCI_RAHASIA)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Mengambil input dari form (Pastikan key sesuai dengan atribut 'name' di HTML)
        nama_dosen = request.form.get('nama_dosen')
        matkul = request.form.get('matkul')
        kategori = request.form.get('kategori')
        kronologi_asli = request.form.get('kronologi')
        
        try:
            # ====================================================
            # 🔮 PROSES KRIPTOGRAFI 1: ENKRIPSI (Plaintext -> Ciphertext)
            # ====================================================
            # Teks asli (string) diubah ke bentuk bytes dengan encoding UTF-8
            plaintext_bytes = kronologi_asli.encode('utf-8')
            # Proses pengacakan menggunakan algoritma AES-128 via Fernet
            ciphertext_bytes = fernet.encrypt(plaintext_bytes)
            # Mengubah hasil enkripsi (bytes) kembali ke string agar aman dikirim ke HTML
            kronologi_terenkripsi = ciphertext_bytes.decode('utf-8')
            
            # ====================================================
            # 🔮 PROSES KRIPTOGRAFI 2: DEKRIPSI (Ciphertext -> Plaintext)
            # ====================================================
            # Memulihkan kembali teks acak menggunakan kunci rahasia yang sama
            decrypted_bytes = fernet.decrypt(ciphertext_bytes)
            kronologi_dekripsi = decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            kronologi_terenkripsi = f"[Gagal Enkripsi: {str(e)}]"
            kronologi_dekripsi = "[Gagal Dekripsi]"

        # Mengirimkan semua data hasil pemrosesan ke halaman response.html
        return render_template('response.html', 
                               nama_dosen=nama_dosen, 
                               matkul=matkul, 
                               kategori=kategori, 
                               laporan_asli=kronologi_asli,
                               laporan_terenkripsi=kronologi_terenkripsi,
                               laporan_dekripsi=kronologi_dekripsi)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)