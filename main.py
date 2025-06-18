from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'secret'

def hitungPotensial(minat, relevansi, reputasi):
    return round((minat + relevansi + reputasi) / 3, 2)

def knapsackDP(mk_list, max_sks):
    n = len(mk_list)
    weights = []
    values = []
    for mk in mk_list:
        weights.append(mk["sks"])
        values.append(mk["nilai_potensial"])
    
    dp = [None] * n
    for i in range(0, n, 1):
        dp[i] = [None] * (max_sks + 1)

    for i in range(n):
        for w in range(max_sks + 1):
            if weights[i] <= w:
                if i == 0:
                    dp[i][w] = values[i]
                else:
                    dp[i][w] = max(dp[i - 1][w], values[i] + dp[i - 1][w - weights[i]])
            else:
                if i == 0:
                    dp[i][w] = 0
                else:
                    dp[i][w] = dp[i - 1][w]

    w = max_sks
    selected = []
    for i in range(n - 1, -1, -1):
        if i == 0:
            if dp[i][w] != 0:
                selected.append(i)
        elif dp[i][w] != dp[i - 1][w]:
            selected.append(i)
            w -= weights[i]

    selected.reverse()

    total_sks = 0
    total_value = 0
    selected_mk = []
    for i in selected:
        total_sks += weights[i]
        total_value += values[i]
        selected_mk.append(mk_list[i])

    return {
        "total_sks": total_sks,
        "total_value": round(total_value, 2),
        "selected": selected_mk
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'mata_kuliah' not in session:
        session['mata_kuliah'] = []

    mata_kuliah = session['mata_kuliah']
    hasil = None
    error = None

    if request.method == 'POST':
        if('tambah' in request.form):
            try:
                nama = request.form['nama']
                sks = int(request.form['sks'])
                minat = int(request.form['minat'])
                relevansi = int(request.form['relevansi'])
                reputasi = int(request.form['reputasi'])

                if not (1 <= minat <= 10 and 1 <= relevansi <= 10 and 1 <= reputasi <= 10):
                    error = "Nilai minat, relevansi, dan reputasi harus 1–10"
                elif(sks <= 0 or sks > 24):
                    error = "SKS harus antara 1–24"
                else:
                    mk = {
                        "nama": nama,
                        "sks": sks,
                        "minat": minat,
                        "relevansi": relevansi,
                        "reputasi": reputasi,
                        "nilai_potensial": hitungPotensial(minat, relevansi, reputasi)
                    }
                    mata_kuliah.append(mk)
                    session['mata_kuliah'] = mata_kuliah
                    return redirect(url_for('index'))
            except ValueError:
                error = "Pastikan semua input numerik valid!"

        elif('hapus' in request.form):
            idx = int(request.form.get('hapus_index', -1))
            if 0 <= idx < len(mata_kuliah):
                mata_kuliah.pop(idx)
                session['mata_kuliah'] = mata_kuliah
                return redirect(url_for('index'))

        elif('proses' in request.form):
            try:
                max_sks = int(request.form['max_sks'])
                if len(mata_kuliah) < 8:
                    error = "Masukkan minimal 8 mata kuliah sebelum memproses!"
                elif max_sks <= 0:
                    error = "Batas maksimal SKS harus lebih dari 0"
                else:
                    hasil = knapsackDP(mata_kuliah, max_sks)
            except ValueError:
                error = "Masukkan nilai SKS maksimal yang valid!"

        elif('reset' in request.form):
            session.pop('mata_kuliah', None)
            return redirect(url_for('index'))

    return render_template('index.html', mata_kuliah=mata_kuliah, hasil=hasil, error=error)

if __name__ == '__main__':
    app.run(debug=True)