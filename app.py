from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import json
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Güvenli gizli anahtar
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

KULLANICI_ADI = "Helium"
AYAR_DOSYASI = "ayarlar.json"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def ayarlari_oku():
    if not os.path.exists(AYAR_DOSYASI):
        return {
            "sifre": "123456"
        }

    with open(AYAR_DOSYASI, "r", encoding="utf-8") as dosya:
        return json.load(dosya)


def mevcut_sifre():
    # Render'da Environment Variable kullanılır
    render_sifresi = os.environ.get("ADMIN_PASSWORD")

    if render_sifresi:
        return render_sifresi

    # Bilgisayarda çalışırken ayarlar.json kullanılır
    ayarlar = ayarlari_oku()
    return ayarlar["sifre"]


def izin_verilen_dosya(dosya_adi):
    return (
        "." in dosya_adi
        and dosya_adi.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/")
def ana_sayfa():
    return render_template("index.html")


@app.route("/anilar")
def anilar():
    fotograflar = []

    if os.path.exists(UPLOAD_FOLDER):
        fotograflar = os.listdir(UPLOAD_FOLDER)

    return render_template(
        "anilar.html",
        fotograflar=fotograflar
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


@app.route("/yonetim")
def yonetim():
    if "kullanici" not in session:
        return redirect(url_for("giris"))

    fotograflar = []

    if os.path.exists(UPLOAD_FOLDER):
        fotograflar = os.listdir(UPLOAD_FOLDER)

    return render_template(
        "yonetim.html",
        fotograflar=fotograflar
    )


@app.route("/giris", methods=["GET", "POST"])
def giris():
    if request.method == "POST":

        kullanici = request.form["username"]
        sifre = request.form["password"]

        if kullanici == KULLANICI_ADI and sifre == mevcut_sifre():
            session["kullanici"] = kullanici
            return redirect(url_for("yonetim"))

        return "Kullanıcı adı veya şifre yanlış!"

    return render_template("login.html")


@app.route("/fotoğraf-yukle", methods=["POST"])
def fotograf_yukle():

    if "kullanici" not in session:
        return redirect(url_for("giris"))

    dosya = request.files.get("fotoğraf")

    if not dosya or dosya.filename == "":
        return "Fotoğraf seçilmedi!"

    if not izin_verilen_dosya(dosya.filename):
        return "Bu dosya türüne izin verilmiyor!"

    dosya_adi = secure_filename(dosya.filename)

    dosya.save(
        os.path.join(
            app.config["UPLOAD_FOLDER"],
            dosya_adi
        )
    )

    return redirect(url_for("yonetim"))


@app.route("/fotoğraf-sil/<filename>", methods=["POST"])
def fotograf_sil(filename):

    if "kullanici" not in session:
        return redirect(url_for("giris"))

    dosya_yolu = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if os.path.exists(dosya_yolu):
        os.remove(dosya_yolu)

    return redirect(url_for("yonetim"))


@app.route("/sifre-degistir", methods=["POST"])
def sifre_degistir():

    if "kullanici" not in session:
        return redirect(url_for("giris"))

    # Render'da Environment Variable doğrudan uygulama tarafından değiştirilemez.
    if os.environ.get("ADMIN_PASSWORD"):
        return "Şifreyi değiştirmek için Render > Environment > Environment Variables bölümündeki ADMIN_PASSWORD değerini değiştir."

    eski_sifre = request.form["eski_sifre"]
    yeni_sifre = request.form["yeni_sifre"]
    yeni_sifre_tekrar = request.form["yeni_sifre_tekrar"]

    ayarlar = ayarlari_oku()

    if eski_sifre != ayarlar["sifre"]:
        return "Mevcut şifre yanlış!"

    if yeni_sifre != yeni_sifre_tekrar:
        return "Yeni şifreler aynı değil!"

    if len(yeni_sifre) < 6:
        return "Yeni şifre en az 6 karakter olmalı!"

    ayarlar["sifre"] = yeni_sifre

    with open(AYAR_DOSYASI, "w", encoding="utf-8") as dosya:
        json.dump(
            ayarlar,
            dosya,
            ensure_ascii=False,
            indent=4
        )

    return "Şifre başarıyla değiştirildi!"


@app.route("/cikis")
def cikis():
    session.clear()
    return redirect(url_for("ana_sayfa"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )