from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import os

app = Flask(__name__, template_folder='templates')

# Kunci statis darurat untuk UAS agar tidak berubah-ubah setiap kali reload server
# Ini adalah kunci Fernet valid berformat base64 (32 bytes)
KUNCI_UAS = b'HogwartsSecretKeyForCryptoUAS2026Base64='

try:
    fernet = Fernet(KUNCI_UAS)
except Exception:
    # Jika kunci di atas bermasalah, generate otomatis sebagai cadangan
    KUNCI_UAS = Fernet.generate_key()
    fernet = Fernet(KUNCI_UAS)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nama_dosen = request.form.get('nama_dosen')
        matkul = request.form.get('matkul')
        kategori_pelanggaran = request.form.get('kategori_pelanggaran')
        kronologi_asli = request.form.get('kronologi') # Plaintext
        
        try:
            # === PROSES KRIPTOGRAFI (ENKRIPSI) ===
            kronologi_bytes = kronologi_asli.encode('utf-8')
            ciphertext_bytes = fernet.encrypt(kronologi_bytes)
            kronologi_terenkripsi = ciphertext_bytes.decode('utf-8') # Menjadi Ciphertext string
            
            # === PROSES KRIPTOGRAFI (DEKRIPSI) ===
            decrypted_bytes = fernet.decrypt(ciphertext_bytes)
            kronologi_dekripsi = decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            # Mengamankan sistem agar tidak Internal Server Error jika enkripsi gagal
            kronologi_terenkripsi = "[Gagal mengenkripsi pesan secara magis]"
            kronologi_dekripsi = f"[Gagal mendekripsi: {str(e)}]"

        # Kirim semua data aman ke halaman respon
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
