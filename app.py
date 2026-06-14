from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__, template_folder='templates')

# Kunci Fernet valid 32-bytes Base64
KUNCI_RAHASIA = b'6fX59pW8Z9_n3NvZ7Wd1Y5_K6e1S_M2b3C4d5E6f7G8='
fernet = Fernet(KUNCI_RAHASIA)

DB_FILE = 'database_aduan.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aduan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_dosen TEXT NOT NULL,
            matkul TEXT NOT NULL,
            kategori TEXT NOT NULL,
            laporan_terenkripsi TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Jalankan inisialisasi database
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nama_dosen = request.form.get('nama_dosen')
        matkul = request.form.get('matkul')
        kategori = request.form.get('kategori')
        kronologi_asli = request.form.get('kronologi')
        
        try:
            # === PROSES 1: ENKRIPSI ===
            plaintext_bytes = kronologi_asli.encode('utf-8')
            ciphertext_bytes = fernet.encrypt(plaintext_bytes)
            kronologi_terenkripsi = ciphertext_bytes.decode('utf-8')
            
            # SIMPAN KE DATABASE
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO aduan (nama_dosen, matkul, kategori, laporan_terenkripsi)
                VALUES (?, ?, ?, ?)
            ''', (nama_dosen, matkul, kategori, kronologi_terenkripsi))
            conn.commit()
            conn.close()
            
            # === PROSES 2: DEKRIPSI ===
            decrypted_bytes = fernet.decrypt(ciphertext_bytes)
            kronologi_dekripsi = decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            kronologi_terenkripsi = f"[Gagal Enkripsi: {str(e)}]"
            kronologi_dekripsi = "[Gagal Dekripsi]"

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