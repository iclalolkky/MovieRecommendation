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
        self.setGeometry(100, 100, 1100, 600)

        # Modern Karanlık Tema (Dark Mode) Stilleri
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QListWidget, QTableWidget {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 5px;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item:selected, QTableWidget::item:selected {
                background-color: #89b4fa;
                color: #11111b;
            }
            QHeaderView::section {
                background-color: #45475a;
                color: #cdd6f4;
                padding: 5px;
                font-weight: bold;
                border: none;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        # Sınıf değişkenleri
        self.df = pd.DataFrame()
        self.genre_columns = []
        self.platform_columns = []

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
            self.genre_columns = [col for col in self.df.columns if col.startswith('genres_')]
            self.platform_columns = [col for col in self.df.columns if col.startswith('platforms_')]
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
        display_genres = [col.replace('genres_', '').replace('_', ' ') for col in self.genre_columns]
        self.genre_list.addItems(display_genres)
        genre_layout.addWidget(genre_label)
        genre_layout.addWidget(self.genre_list)
        filter_layout.addLayout(genre_layout)

        # Platform Filtresi (Çoklu Seçim)
        platform_layout = QVBoxLayout()
        platform_label = QLabel("Platformlar:")
        self.platform_list = QListWidget()
        self.platform_list.setSelectionMode(QAbstractItemView.MultiSelection)
        display_platforms = [col.replace('platforms_', '').replace('_', ' ').title() for col in self.platform_columns]
        self.platform_list.addItems(display_platforms)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_list)
        filter_layout.addLayout(platform_layout)

        self.main_layout.addLayout(filter_layout)

        # Filtrele Butonu
        self.filter_btn = QPushButton("Filmleri Filtrele")
        self.filter_btn.clicked.connect(self.filter_movies)
        self.main_layout.addWidget(self.filter_btn)

        # --- Orta Kısım: Tablo ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Başlık", "Yıl", "IMDB Puanı", "Türler", "Platformlar"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Türler uzasın
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Platform uzasın
        self.main_layout.addWidget(self.table)

        # --- Alt Kısım: İstatistikler ---
        stats_layout = QHBoxLayout()
        self.mean_label = QLabel("Ortalama IMDB: -")
        self.median_label = QLabel("Medyan IMDB: -")

        font = self.mean_label.font()
        font.setBold(True)
        self.mean_label.setFont(font)
        self.median_label.setFont(font)

        stats_layout.addWidget(self.mean_label)
        stats_layout.addWidget(self.median_label)
        self.main_layout.addLayout(stats_layout)

    def filter_movies(self):
        min_year = self.year_spinbox.value()
        min_imdb = self.imdb_spinbox.value()

        selected_genre_items = self.genre_list.selectedItems()
        selected_genres = [item.text() for item in selected_genre_items]

        selected_platform_items = self.platform_list.selectedItems()
        selected_platforms = [item.text().lower().replace(' ', '_') for item in selected_platform_items]

        filtered_df = self.df.copy()
        filtered_df = filtered_df.dropna(subset=['year', 'imdb_score'])

        # Yıl ve IMDB Filtresi
        filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['imdb_score'] >= min_imdb)]

        # Tür Filtresi
        if selected_genres:
            valid_genre_cols = ['genres_' + g.replace(' ', '_') for g in selected_genres]
            valid_genre_cols = [col for col in valid_genre_cols if col in filtered_df.columns]
            if valid_genre_cols:
                filtered_df = filtered_df[filtered_df[valid_genre_cols].sum(axis=1) > 0]

        # Platform Filtresi
        if selected_platforms:
            valid_platform_cols = ['platforms_' + p for p in selected_platforms]
            valid_platform_cols = [col for col in valid_platform_cols if col in filtered_df.columns]
            if valid_platform_cols:
                filtered_df = filtered_df[filtered_df[valid_platform_cols].sum(axis=1) > 0]

        # Tabloyu Doldur
        self.table.setRowCount(0)
        for index, row in filtered_df.iterrows():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)

            movie_genres = [col.replace('genres_', '').replace('_', ' ') for col in self.genre_columns if
                            pd.notna(row[col]) and row[col] > 0]
            genres_str = ", ".join(movie_genres)

            movie_platforms = [col.replace('platforms_', '').replace('_', ' ').title() for col in self.platform_columns
                               if pd.notna(row[col]) and row[col] > 0]
            platforms_str = ", ".join(movie_platforms)

            self.table.setItem(row_pos, 0, QTableWidgetItem(str(row['title'])))
            self.table.setItem(row_pos, 1, QTableWidgetItem(str(int(row['year']))))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(row['imdb_score'])))
            self.table.setItem(row_pos, 3, QTableWidgetItem(genres_str))
            self.table.setItem(row_pos, 4, QTableWidgetItem(platforms_str))

        # İstatistikler
        if not filtered_df.empty:
            mean_imdb = filtered_df['imdb_score'].mean()
            median_imdb = filtered_df['imdb_score'].median()
            self.mean_label.setText(f"Ortalama IMDB: {mean_imdb:.2f}")
            self.median_label.setText(f"Medyan IMDB: {median_imdb:.2f}")
        else:
            self.mean_label.setText("Ortalama IMDB: -")
            self.median_label.setText("Medyan IMDB: -")

# UYGULAMAYI ÇALIŞTIRAN BLOK (EN SOLA HİZALANDI)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilmOneriApp()
    window.show()
    sys.exit(app.exec_())