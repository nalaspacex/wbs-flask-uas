from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__, template_folder='templates')

# GENERATE KUNCI KRIPTOGRAFI
# Di dunia nyata, kunci ini disimpan rahasia di Environment Variable
KUNCI_RAHASIA = Fernet.generate_key()
fernet = Fernet(KUNCI_RAHASIA)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nama_dosen = request.form.get('nama_dosen')
        matkul = request.form.get('matkul')
        kategori_pelanggaran = request.form.get('kategori_pelanggaran')
        kronologi_asli = request.form.get('kronologi') # Plaintext
        
        # === PROSES KRIPTOGRAFI (ENKRIPSI) ===
        # Teks biasa diubah menjadi bytes, lalu dienkripsi menjadi Ciphertext
        kronologi_bytes = kronologi_asli.encode()
        ciphertext_bytes = fernet.encrypt(kronologi_bytes)
        kronologi_terenkripsi = ciphertext_bytes.decode() # Mengubah hasil enkripsi ke string agar bisa dikirim
        
        # === PROSES KRIPTOGRAFI (DEKRIPSI) ===
        # Mensimulasikan admin membaca kembali laporan asli menggunakan kunci yang sama
        decrypted_bytes = fernet.decrypt(ciphertext_bytes)
        kronologi_dekripsi = decrypted_bytes.decode()

        # Kirim data teks asli, teks enkripsi, dan hasil dekripsi ke halaman respon
        return render_template('response.html', 
                               nama_dosen=nama_dosen, 
                               matkul=matkul, 
                               kategori=kategori_pelanggaran, 
                               laporan_asli=kronologi_asli,
                               laporan_terenkripsi=kronologi_terenkripsi,
                               laporan_dekripsi=kronologi_dekripsi)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)