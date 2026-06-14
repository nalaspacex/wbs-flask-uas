from flask import Flask, render_template, request, redirect, url_for
import os
import sqLite3

app = Flask(__name__)
DB_FILE = "wbs_database.db"


def encrypt_text(text, shift=5):
    result = ""
    for char in text:
        if char.isalpha():
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aduan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategori TEXT NOT NULL,
            laporan_terenkripsi TEXT NOT NULL,
            waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        kategori = request.form.get('kategori', '')
        laporan_asli = request.form.get('laporan', '')
        
        # Enkripsi teks laporan sebelum masuk database agar admin pun tidak bisa baca langsung
        laporan_secure = encrypt_text(laporan_asli)
        
        # Simpan ke Database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO aduan (kategori, laporan_terenkripsi) VALUES (?, ?)", 
            (kategori, laporan_secure)
        )
        conn.commit()
        conn.close()
        
        return render_template('response.html', kategori=kategori, laporan_secure=laporan_secure)

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("SELECT id, kategori, laporan_terenkripsi, waktu FROM aduan ORDER BY id DESC")
daftar_aduan = cursor.fetchall()
conn.close()
    
return render_template('form.html', aduan_data=daftar_aduan)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)