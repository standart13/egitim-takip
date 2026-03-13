import pandas as pd
import json
import sys

def main():
    try:
        df = pd.read_csv('personel_egitim.csv', header=1)
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)

    employees = []
    
    col_mapping = {
        't1': 5, 't2': 6, 't3': 7, 't4': 8,
        't5': 9, 't8': 10, 't6': 11, 't7': 12
    }

    for index, row in df.iterrows():
        sicil = str(row.iloc[0]).strip()
        name = str(row.iloc[1]).strip()
        
        if pd.isna(row.iloc[0]) or sicil == 'nan' or name == 'nan':
            continue
        
        bolum_kodu = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
        dept_kodu = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
        
        records = {}
        for t_id, col_idx in col_mapping.items():
            if col_idx < len(row):
                date_val = str(row.iloc[col_idx]).strip()
                if pd.notna(row.iloc[col_idx]) and date_val != 'nan' and not date_val.startswith('1899'):
                    if len(date_val) >= 10 and date_val[0:4].isdigit():
                        records[t_id] = date_val[0:10]
                    
        employees.append({
            'id': index + 1000,
            'sicil': sicil.split('.')[0] if sicil.endswith('.0') else sicil,
            'name': name,
            'bolumKodu': bolum_kodu.split('.')[0] if bolum_kodu.endswith('.0') else bolum_kodu,
            'deptKodu': dept_kodu.split('.')[0] if dept_kodu.endswith('.0') else dept_kodu,
            'records': records
        })

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(employees, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
    main()