import pandas as pd
import json
import os

def process_csv():
    csv_file = 'personel_egitim.csv'
    if not os.path.exists(csv_file):
        print(f"Hata: {csv_file} bulunamadı.")
        return

    try:
        # Veriyi oku ve başlıkları temizle
        df = pd.read_csv(csv_file, header=1)
        df.columns = df.columns.str.strip()
        
        data = []
        
        # Sütun indekslerini tespit et
        cols = df.columns.tolist()
        sicil_idx = next((i for i, c in enumerate(cols) if 'Sicil' in c), -1)
        name_idx = next((i for i, c in enumerate(cols) if 'Adı Soyadı' in c), -1)
        bolum_idx = next((i for i, c in enumerate(cols) if 'Bölüm Kodu' in c), -1)
        dept_idx = next((i for i, c in enumerate(cols) if 'Dpt. Kodu' in c), -1)

        def clean_val(val):
            if pd.isna(val): return ""
            # Sayısal verilerin sonundaki .0 kısmını atar ve metne çevirir
            s = str(val).split('.')[0].strip()
            return "" if s.lower() == 'nan' else s

        for _, row in df.iterrows():
            if sicil_idx != -1 and pd.notna(row.iloc[sicil_idx]):
                entry = {
                    "sicil": clean_val(row.iloc[sicil_idx]),
                    "adSoyad": str(row.iloc[name_idx]).strip() if name_idx != -1 else "",
                    "bolumKodu": clean_val(row.iloc[bolum_idx]) if bolum_idx != -1 else "",
                    "deptKodu": clean_val(row.iloc[dept_idx]) if dept_idx != -1 else "",
                    "egitimler": []
                }
                
                # Eğitim sütunlarını tara (8. sütundan sonrası)
                for col_name in cols[8:]:
                    val = row[col_name]
                    if pd.notna(val) and str(val).strip() != "":
                        entry["egitimler"].append({
                            "ad": col_name,
                            "tarih": str(val).strip()
                        })
                data.append(entry)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("data.json başarıyla oluşturuldu.")

    except Exception as e:
        print(f"İşlem sırasında hata: {e}")

if __name__ == "__main__":
    process_csv()
