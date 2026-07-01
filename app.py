from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'kunci_sesi_rahasia_untuk_flash_message'

# Kunci Fernet valid 32-bytes Base64
KUNCI_RAHASIA = b'6fX59pW8Z9_n3NvZ7Wd1Y5_K6e1S_M2b3C4d5E6f7G8='
fernet = Fernet(KUNCI_RAHASIA)

DB_FILE = 'database_aduan.db'

# Data Login Admin Terbatas (Bisa disesuaikan)
ADMIN_USERNAME = "admin_hogwarts"
ADMIN_PASSWORD = "agent007"

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
            # === 🔮 ENKRIPSI DATA SEBELUM MASUK DATABASE ===
            enc_nim = fernet.encrypt(nim_asli.encode('utf-8')).decode('utf-8')
            enc_kronologi = fernet.encrypt(kronologi_asli.encode('utf-8')).decode('utf-8')
            
            # SIMPAN KE DATABASE SQLITE
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO aduan (nama_dosen, matkul, kategori, nim_terenkripsi, laporan_terenkripsi)
                VALUES (?, ?, ?, ?, ?)
            ''', (nama_dosen, matkul, kategori, enc_nim, enc_kronologi))
            conn.commit()
            conn.close()
            
            
        except Exception as e:
            # Jika tetap gagal, tampilkan detail pesan error asli dari compiler Python
            enc_nim = f"[Gagal Enkripsi NIM: {str(e)}]"
            enc_kronologi = f"[Gagal Enkripsi Laporan: {str(e)}]"

        return render_template('response.html', 
                               nama_dosen=nama_dosen, 
                               matkul=matkul, 
                               kategori=kategori, 
                               nim_asli=nim_asli,
                               nim_terenkripsi=enc_nim,
                               laporan_asli=kronologi_asli,
                               laporan_terenkripsi=enc_kronologi,
    
    return render_template('form.html')

# 2. HALAMAN LOGIN ADMIN (OTENTIKASI)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Username atau Password Salah!")
            return redirect(url_for('login'))
            
    return render_template('login.html')

# 3. HALAMAN DASHBOARD RIWAYAT (HANYA UNTUK ADMIN TEROTENTIKASI)
@app.route('/dashboard')
def dashboard():
    # Proteksi Keamanan: Jika belum login, tendang kembali ke halaman login
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nama_dosen, matkul, kategori, nim_terenkripsi, laporan_terenkripsi, timestamp FROM aduan ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    riwayat_aduan = []
    for row in rows:
        try:
            # === 🔮 PROSES DEKRIPSI OTOMATIS OLEH UTORITAS ADMIN ===
            dec_nim = fernet.decrypt(row[4].encode('utf-8')).decode('utf-8')
            dec_kronologi = fernet.decrypt(row[5].encode('utf-8')).decode('utf-8')
        except:
            dec_nim = "[Gagal Dekripsi]"
            dec_kronologi = "[Gagal Dekripsi]"
            
        riwayat_aduan.append({
            'id': row[0],
            'nama_dosen': row[1],
            'matkul': row[2],
            'kategori': row[3],
            'nim_terenkripsi': row[4],
            'nim_dekripsi': dec_nim,
            'laporan_terenkripsi': row[5],
            'laporan_dekripsi': dec_kronologi,
            'waktu': row[6]
        })
        
    return render_template('dashboard.html', aduan_list=riwayat_aduan)

# 4. ROUTE LOGOUT ADMIN
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)