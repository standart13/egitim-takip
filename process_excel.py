import pandas as pd
import json
import os
import sys

def clean_val(val):
    if pd.isna(val): return ""
    s = str(val).split('.')[0].strip()
    return "" if s.lower() == 'nan' else s

def process_csv():
    csv_file = 'personel_egitim.csv'
    if not os.path.exists(csv_file):
        print("Hata: personel_egitim.csv bulunamadı.")
        sys.exit(1)

    try:
        # CSV UTF-8 (Virgülle ayrılmış) okuma
        df = pd.read_csv(csv_file, header=1)
        df.columns = df.columns.str.strip()
        
        data = []
        cols = df.columns.tolist()
        
        # Sütun tespiti
        sicil_col = next((c for c in cols if 'Sicil' in c), None)
        name_col = next((c for c in cols if 'Adı Soyadı' in c), None)
        bolum_col = next((c for c in cols if 'Bölüm Kodu' in c), None)
        dept_col = next((c for c in cols if 'Dept' in c or 'Dpt' in c), None)

        for _, row in df.iterrows():
            sicil = clean_val(row[sicil_col]) if sicil_col else ""
            if not sicil: continue
            
            entry = {
                "sicil": sicil,
                "name": str(row[name_col]).strip() if name_col else "",
                "bolumKodu": clean_val(row[bolum_col]) if bolum_col else "",
                "deptKodu": clean_val(row[dept_col]) if dept_col else "",
                "records": {}
            }
            
            # Eğitimleri işle (5. sütundan itibaren tarih arama)
            for i in range(5, len(cols)):
                col_name = cols[i]
                val = row[col_name]
                if pd.notna(val) and str(val).strip() != "" and "Unnamed" not in col_name:
                    # Eğitim ID eşleştirme veya direkt isim kullanma
                    entry["records"][col_name] = str(val).strip()
            
            data.append(entry)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Veri başarıyla data.json dosyasına işlendi.")

    except Exception as e:
        print(f"Hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_csv()
