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
            nim_terenkripsi TEXT NOT NULL,
            laporan_terenkripsi TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Menggunakan cadangan string kosong "" jika form mengirimkan None
        nama_dosen = request.form.get('nama_dosen', '')
        matkul = request.form.get('matkul', '')
        kategori = request.form.get('kategori', '')
        nim_asli = request.form.get('nim_mahasiswa', '')
        kronologi_asli = request.form.get('kronologi', '')
        
        try:
            # === 🔮 PROSES KRIPTOGRAFI: ENKRIPSI ===
            enc_nim = fernet.encrypt(nim_asli.encode('utf-8')).decode('utf-8')
            enc_kronologi = fernet.encrypt(kronologi_asli.encode('utf-8')).decode('utf-8')
            
            # SIMPAN DATA KE DATABASE
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO aduan (nama_dosen, matkul, kategori, nim_terenkripsi, laporan_terenkripsi)
                VALUES (?, ?, ?, ?, ?)
            ''', (nama_dosen, matkul, kategori, enc_nim, enc_kronologi))
            conn.commit()
            conn.close()
            
            # === 🔮 PROSES KRIPTOGRAFI: DEKRIPSI ===
            dec_nim = fernet.decrypt(enc_nim.encode('utf-8')).decode('utf-8')
            dec_kronologi = fernet.decrypt(enc_kronologi.encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            # Jika tetap gagal, tampilkan detail pesan error asli dari compiler Python
            enc_nim = f"[Gagal Enkripsi NIM: {str(e)}]"
            enc_kronologi = f"[Gagal Enkripsi Laporan: {str(e)}]"
            dec_nim = "[Gagal Dekripsi]"
            dec_kronologi = "[Gagal Dekripsi]"

        return render_template('response.html', 
                               nama_dosen=nama_dosen, 
                               matkul=matkul, 
                               kategori=kategori, 
                               nim_asli=nim_asli,
                               nim_terenkripsi=enc_nim,
                               nim_dekripsi=dec_nim,
                               laporan_asli=kronologi_asli,
                               laporan_terenkripsi=enc_kronologi,
                               laporan_dekripsi=dec_kronologi)
    
    return render_template('form.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)