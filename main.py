import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel


class FilmOneriApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.setWindowTitle("Film Öneri Platformu")
        self.setGeometry(100, 100, 800, 600)  # x, y, genişlik, yükseklik

        # Arayüz için geçici bir yazı
        self.test_label = QLabel("Veriler yükleniyor...", self)
        self.test_label.setGeometry(300, 250, 200, 30)

        # Veri setini yükle
        self.load_data()

    def load_data(self):
        try:
            # CSV dosyasını okuyoruz
            self.df = pd.read_csv("HBO_Content.csv")
            print("Veri seti başarıyla yüklendi!")
            print("Sütunlar:", self.df.columns.tolist())  # Verideki başlıkları konsola yazdır

            self.test_label.setText("Veri başarıyla okundu! Konsola bak.")

        except Exception as e:
            print("Dosya okunurken bir hata oluştu:", e)
            self.test_label.setText("Veri okuma hatası!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilmOneriApp()
    window.show()
    sys.exit(app.exec_())