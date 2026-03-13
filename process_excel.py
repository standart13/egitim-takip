import pandas as pd
import json
import sys

def find_training_id(name):
    if not isinstance(name, str): return None
    n = name.upper()
    if 'GENEL KONULAR' in n: return 't1'
    if 'SAĞLIK' in n: return 't2'
    if 'TEKNİK KONULAR 2' in n: return 't4'
    if 'TEKNİK KONULAR 3' in n or '10TK' in n: return 't5'
    if 'TEKNİK KONULAR' in n: return 't3'
    if 'VR ATÖLYE' in n or 'SANAL GERÇEKLİK' in n and 'ATÖLYE' in n: return 't6'
    if 'VR LOJİSTİK' in n or 'SANAL GERÇEKLİK' in n and 'LOJİSTİK' in n: return 't7'
    if 'TİSK' in n: return 't8'
    return None

def parse_excel_date(val):
    try:
        if isinstance(val, (int, float)):
            if val > 40000:
                return (pd.to_datetime('1899-12-30') + pd.to_timedelta(val, 'D')).strftime('%Y-%m-%d')
        elif isinstance(val, str):
            parts = val.split()[0].split('.')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
            return val
    except:
        pass
    return str(val)

def main():
    try:
        df_raw = pd.read_csv('personel_egitim.csv', header=None)
    except Exception as e:
        print(f"Hata: {e}")
        sys.exit(1)

    header_idx = -1
    for i, row in df_raw.iterrows():
        row_str = ' '.join(str(x).lower() for x in row.values)
        if 'sicil' in row_str and ('ad' in row_str or 'soyad' in row_str):
            header_idx = i
            break
            
    if header_idx == -1:
        print("Header row not found")
        sys.exit(1)

    headers = df_raw.iloc[header_idx].fillna('').astype(str).tolist()
    df = df_raw.iloc[header_idx+1:].copy()
    
    def get_col_idx(keywords):
        for i, h in enumerate(headers):
            h_low = h.lower()
            if all(k.lower() in h_low for k in keywords):
                return i
        return -1

    sicil_idx = get_col_idx(['sicil'])
    name_idx = get_col_idx(['ad', 'soyad'])
    egitim_idx = get_col_idx(['eğitim', 'ad'])
    not_idx = get_col_idx(['not']) if get_col_idx(['not']) != -1 else get_col_idx(['puan'])
    tarih_idx = get_col_idx(['tarih'])
    bolum_idx = get_col_idx(['bölüm'])
    dept_idx = get_col_idx(['dept'])

    parsed_employees = {}

    if egitim_idx != -1 and tarih_idx != -1:
        for _, row in df.iterrows():
            if pd.isna(row.iloc[sicil_idx]) or pd.isna(row.iloc[name_idx]): continue
            sicil = str(row.iloc[sicil_idx]).replace('.0', '').strip()
            name = str(row.iloc[name_idx]).strip()
            bolum = str(row.iloc[bolum_idx]).replace('.0', '').strip() if bolum_idx != -1 else ''
            dept = str(row.iloc[dept_idx]).replace('.0', '').strip() if dept_idx != -1 else ''
            
            if sicil not in parsed_employees:
                parsed_employees[sicil] = {'id': sicil, 'sicil': sicil, 'name': name, 'bolumKodu': bolum, 'deptKodu': dept, 'records': {}}
                
            t_id = find_training_id(str(row.iloc[egitim_idx]))
            if t_id and pd.notna(row.iloc[tarih_idx]):
                date_val = parse_excel_date(row.iloc[tarih_idx])
                score = None
                if not_idx != -1 and pd.notna(row.iloc[not_idx]):
                    try: score = float(str(row.iloc[not_idx]).replace(',', '.'))
                    except: pass
                parsed_employees[sicil]['records'][t_id] = {'date': date_val, 'score': score}
    else:
        map_wide = {
           'GENEL KONULAR': 't1', 'SAĞLIK': 't2', 'TEKNİK KONULAR 2': 't4', 
           '10TK': 't5', 'TEKNİK KONULAR': 't3', 'ATÖLYE': 't6', 'LOJİSTİK': 't7', 'TİSK': 't8'
        }
        for i, row in df.iterrows():
            if pd.isna(row.iloc[sicil_idx]) or pd.isna(row.iloc[name_idx]): continue
            sicil = str(row.iloc[sicil_idx]).replace('.0', '').strip()
            name = str(row.iloc[name_idx]).strip()
            bolum = str(row.iloc[bolum_idx]).replace('.0', '').strip() if bolum_idx != -1 else ''
            dept = str(row.iloc[dept_idx]).replace('.0', '').strip() if dept_idx != -1 else ''
            
            emp = {'id': sicil, 'sicil': sicil, 'name': name, 'bolumKodu': bolum, 'deptKodu': dept, 'records': {}}
            
            for h_idx, h_name in enumerate(headers):
                for k, t_id in map_wide.items():
                    if k in h_name.upper():
                        val = row.iloc[h_idx]
                        if pd.notna(val) and str(val).strip() != 'nan':
                            date_val = parse_excel_date(val)
                            score = None
                            if h_idx + 1 < len(headers) and ('NOT' in headers[h_idx+1].upper() or 'PUAN' in headers[h_idx+1].upper()):
                                next_val = row.iloc[h_idx+1]
                                if pd.notna(next_val):
                                    try: score = float(str(next_val).replace(',', '.'))
                                    except: pass
                            if '1899' not in date_val:
                                emp['records'][t_id] = {'date': date_val, 'score': score}
                        break
            parsed_employees[sicil] = emp

    employees_list = list(parsed_employees.values())
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(employees_list, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
    main()
