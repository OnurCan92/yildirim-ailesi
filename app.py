import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

app = Flask(__name__)

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

app.secret_key = "degistir-bu-gizli-anahtari"

KULLANICI_ADI = "Helium"
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# ŞİFRE
# --------------------------------------------------

def mevcut_sifre():

    if os.path.exists("sifre.txt"):

        with open(
            "sifre.txt",
            "r",
            encoding="utf-8"
        ) as dosya:

            return dosya.read()

    return "kimsegiremezburaya152256"


# --------------------------------------------------
# ANA SAYFA
# --------------------------------------------------

@app.route("/")
def ana_sayfa():

    fotograflar = []

    if os.path.exists(UPLOAD_FOLDER):

        fotograflar = os.listdir(
            UPLOAD_FOLDER
        )

    return render_template(
        "index.html",
        fotograflar=fotograflar
    )


# --------------------------------------------------
# ANILAR
# --------------------------------------------------

@app.route("/anilar")
def anilar():

    fotograflar = []

    if os.path.exists(UPLOAD_FOLDER):

        fotograflar = os.listdir(
            UPLOAD_FOLDER
        )

    return render_template(
        "anilar.html",
        fotograflar=fotograflar
    )


# --------------------------------------------------
# FOTOĞRAFLARI GÖRÜNTÜLEME
# --------------------------------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# --------------------------------------------------
# GİRİŞ
# --------------------------------------------------

@app.route("/giris", methods=["GET", "POST"])
def giris():

    if request.method == "POST":

        kullanici = request.form.get(
            "username",
            ""
        )

        sifre = request.form.get(
            "password",
            ""
        )

        if (
            kullanici == KULLANICI_ADI
            and sifre == mevcut_sifre()
        ):

            session["kullanici"] = kullanici

            return redirect(
                url_for("yonetim")
            )

        return "Kullanıcı adı veya şifre yanlış!"

    return render_template(
        "login.html"
    )


# --------------------------------------------------
# YÖNETİM PANELİ
# --------------------------------------------------

@app.route("/yonetim")
def yonetim():

    if "kullanici" not in session:

        return redirect(
            url_for("giris")
        )

    fotograflar = []

    if os.path.exists(UPLOAD_FOLDER):

        fotograflar = os.listdir(
            UPLOAD_FOLDER
        )

    return render_template(
        "yonetim.html",
        fotograflar=fotograflar
    )


# --------------------------------------------------
# ŞİFRE DEĞİŞTİR
# --------------------------------------------------

@app.route("/sifre-degistir", methods=["POST"])
def sifre_degistir():

    if "kullanici" not in session:

        return redirect(
            url_for("giris")
        )

    yeni_sifre = request.form.get(
        "yeni_sifre",
        ""
    )

    yeni_sifre_tekrar = request.form.get(
        "yeni_sifre_tekrar",
        ""
    )

    if yeni_sifre != yeni_sifre_tekrar:

        return "Yeni şifreler aynı değil!"

    if yeni_sifre == "":

        return "Şifre boş bırakılamaz!"

    with open(
        "sifre.txt",
        "w",
        encoding="utf-8"
    ) as dosya:

        dosya.write(
            yeni_sifre
        )

    return """
    <!DOCTYPE html>
    <html lang="tr">

    <head>

        <meta charset="UTF-8">

        <title>Şifre Değiştirildi</title>

    </head>

    <body>

        <div style="
            text-align: center;
            margin-top: 100px;
            font-family: Arial, sans-serif;
        ">

            <div style="
                font-size: 80px;
            ">
                ✅
            </div>

            <h1 style="
                font-size: 42px;
            ">
                Şifre Başarıyla Değiştirildi!
            </h1>

            <p style="
                font-size: 22px;
            ">
                Yeni şifreniz başarıyla kaydedildi.
            </p>

            <br>

            <a
                href="/yonetim"
                style="
                    display: inline-block;
                    padding: 15px 30px;
                    font-size: 20px;
                    text-decoration: none;
                    border-radius: 10px;
                "
            >
                Yönetim Paneline Dön
            </a>

        </div>

    </body>

    </html>
    """


# --------------------------------------------------
# ÇIKIŞ
# --------------------------------------------------

@app.route("/cikis")
def cikis():

    session.pop(
        "kullanici",
        None
    )

    return redirect(
        url_for("giris")
    )


# --------------------------------------------------
# FOTOĞRAF YÜKLEME
# --------------------------------------------------

@app.route("/fotoğraf-yukle", methods=["POST"])
def fotograf_yukle():

    if "kullanici" not in session:

        return redirect(
            url_for("giris")
        )

    dosyalar = request.files.getlist(
        "fotoğraf"
    )

    if not dosyalar:

        return "Fotoğraf seçilmedi!"

    for dosya in dosyalar:

        if dosya.filename == "":

            continue

        dosya_yolu = os.path.join(
            UPLOAD_FOLDER,
            dosya.filename
        )

        dosya.save(
            dosya_yolu
        )

    return redirect(
        url_for("yonetim")
    )


# --------------------------------------------------
# TEK FOTOĞRAF SİLME
# --------------------------------------------------

@app.route(
    "/fotoğraf-sil/<filename>",
    methods=["POST"]
)
def fotograf_sil(filename):

    if "kullanici" not in session:

        return redirect(
            url_for("giris")
        )

    dosya_yolu = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.exists(dosya_yolu):

        os.remove(
            dosya_yolu
        )

    return redirect(
        url_for("yonetim")
    )


# --------------------------------------------------
# TÜM FOTOĞRAFLARI SİLME
# --------------------------------------------------

@app.route(
    "/tum-fotograflari-sil",
    methods=["POST"]
)
def tum_fotograflari_sil():

    if "kullanici" not in session:

        return redirect(
            url_for("giris")
        )

    if os.path.exists(UPLOAD_FOLDER):

        for dosya_adi in os.listdir(UPLOAD_FOLDER):

            dosya_yolu = os.path.join(
                UPLOAD_FOLDER,
                dosya_adi
            )

            if os.path.isfile(dosya_yolu):

                os.remove(
                    dosya_yolu
                )

    return redirect(
        url_for("yonetim")
    )


# --------------------------------------------------
# UYGULAMAYI ÇALIŞTIR
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )