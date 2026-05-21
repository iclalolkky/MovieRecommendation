import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
                             QPushButton, QTableWidget, QListWidget, QAbstractItemView,
                             QTableWidgetItem, QHeaderView)


class FilmOneriApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Film Öneri Platformu")
        self.setGeometry(100, 100, 900, 600)

        # Sınıf değişkenleri
        self.df = pd.DataFrame()
        self.genre_columns = []

        # Veriyi yükle
        self.load_data()

        # Ana Widget ve Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

    def load_data(self):
        try:
            self.df = pd.read_csv("HBO_Content.csv")
            # Tür (genre) sütunlarını tespit et
            self.genre_columns = [col for col in self.df.columns if col.startswith('genres_')]
            print("Veri başarıyla yüklendi!")
        except Exception as e:
            print("Dosya okunurken bir hata oluştu:", e)

    def setup_ui(self):
        # --- Üst Kısım: Filtreler ---
        filter_layout = QHBoxLayout()

        # Yıl Filtresi
        year_layout = QVBoxLayout()
        year_label = QLabel("Minimum Yıl:")
        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(1900, 2030)
        self.year_spinbox.setValue(2010)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_spinbox)
        filter_layout.addLayout(year_layout)

        # IMDB Filtresi
        imdb_layout = QVBoxLayout()
        imdb_label = QLabel("Minimum IMDB:")
        self.imdb_spinbox = QDoubleSpinBox()
        self.imdb_spinbox.setRange(0.0, 10.0)
        self.imdb_spinbox.setSingleStep(0.1)
        self.imdb_spinbox.setValue(7.0)
        imdb_layout.addWidget(imdb_label)
        imdb_layout.addWidget(self.imdb_spinbox)
        filter_layout.addLayout(imdb_layout)

        # Tür Filtresi (Çoklu Seçim)
        genre_layout = QVBoxLayout()
        genre_label = QLabel("Türler:")
        self.genre_list = QListWidget()
        self.genre_list.setSelectionMode(QAbstractItemView.MultiSelection)

        # Veri setinden çektiğimiz tür isimlerini düzenleyip listeye ekliyoruz
        display_genres = [col.replace('genres_', '').replace('_', ' ') for col in self.genre_columns]
        self.genre_list.addItems(display_genres)

        genre_layout.addWidget(genre_label)
        genre_layout.addWidget(self.genre_list)
        filter_layout.addLayout(genre_layout)

        self.main_layout.addLayout(filter_layout)

        # Filtrele Butonu
        self.filter_btn = QPushButton("Filmleri Filtrele")
        self.filter_btn.clicked.connect(self.filter_movies)
        self.main_layout.addWidget(self.filter_btn)

        # --- Orta Kısım: Tablo ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Başlık", "Yıl", "IMDB Puanı", "Türler"])
        # Başlık sütunu ekranı kaplayacak şekilde uzasın
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.main_layout.addWidget(self.table)

        # --- Alt Kısım: İstatistikler ---
        stats_layout = QHBoxLayout()
        self.mean_label = QLabel("Ortalama IMDB: -")
        self.median_label = QLabel("Medyan IMDB: -")

        # İstatistik yazılarını belirginleştir
        font = self.mean_label.font()
        font.setBold(True)
        self.mean_label.setFont(font)
        self.median_label.setFont(font)

        stats_layout.addWidget(self.mean_label)
        stats_layout.addWidget(self.median_label)
        self.main_layout.addLayout(stats_layout)

    def filter_movies(self):
        # 1. Arayüzden kullanıcı seçimlerini al
        min_year = self.year_spinbox.value()
        min_imdb = self.imdb_spinbox.value()

        selected_items = self.genre_list.selectedItems()
        selected_genres = [item.text() for item in selected_items]

        # Orijinal veriyi bozmamak için kopyasını alıyoruz
        filtered_df = self.df.copy()

        # Eksik veri (NaN) olan satırları temizle (Yıl ve IMDB için)
        filtered_df = filtered_df.dropna(subset=['year', 'imdb_score'])

        # 2. Yıl ve IMDB Filtrelemesi
        filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['imdb_score'] >= min_imdb)]

        # 3. Tür Filtrelemesi (DÜZELTİLDİ: VEYA mantığı eklendi)
        if selected_genres:
            valid_cols = []
            for genre in selected_genres:
                col_name = 'genres_' + genre.replace(' ', '_')
                if col_name in filtered_df.columns:
                    valid_cols.append(col_name)

            # Seçilen türlerden "en az birine" sahip olan filmleri filtrele
            if valid_cols:
                filtered_df = filtered_df[filtered_df[valid_cols].sum(axis=1) > 0]

        # 4. Tabloyu Temizle ve Verilerle Doldur
        self.table.setRowCount(0)

        for index, row in filtered_df.iterrows():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)

            # Bu filmin türlerini tespit edip aralarında virgülle bir string oluştur
            movie_genres = []
            for col in self.genre_columns:
                if pd.notna(row[col]) and row[col] > 0:
                    movie_genres.append(col.replace('genres_', '').replace('_', ' '))
            genres_str = ", ".join(movie_genres)

            # Hücreleri doldur
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(row['title'])))
            self.table.setItem(row_pos, 1, QTableWidgetItem(str(int(row['year']))))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(row['imdb_score'])))
            self.table.setItem(row_pos, 3, QTableWidgetItem(genres_str))

        # 5. İstatistikleri Hesapla ve Ekrana Yazdır
        if not filtered_df.empty:
            mean_imdb = filtered_df['imdb_score'].mean()
            median_imdb = filtered_df['imdb_score'].median()

            self.mean_label.setText(f"Ortalama IMDB: {mean_imdb:.2f}")
            self.median_label.setText(f"Medyan IMDB: {median_imdb:.2f}")
        else:
            self.mean_label.setText("Ortalama IMDB: -")
            self.median_label.setText("Medyan IMDB: -")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilmOneriApp()
    window.show()
    sys.exit(app.exec_())