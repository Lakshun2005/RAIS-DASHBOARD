"""
Data Loader Module for RAIS Dashboard
Reads and cleans data from uploaded Excel file buffers.
UPDATED: Works with Streamlit file upload (BytesIO buffers).
"""

import pandas as pd
from datetime import datetime
from io import BytesIO


def load_trend_data(file_buffer) -> pd.DataFrame:
    """
    Loads Monthly Production vs. Rejection Trend data from uploaded file.
    Source: YEARLY PRODUCTION COMMULATIVE 2025-26.xlsx
    """
    if file_buffer is None:
        return pd.DataFrame({'Month': [], 'Production_Qty': [], 'Rejection_Rate': []})
    
    # Read with header at row 2
    df = pd.read_excel(file_buffer, header=2)
    
    # Find column names flexibly (handle variations)
    def find_col(df, keywords):
        for col in df.columns:
            col_str = str(col).upper()
            for kw in keywords:
                if kw.upper() in col_str:
                    return col
        return None
    
    sno_col = find_col(df, ['S.NO', 'SNO', 'S NO', 'SR'])
    month_col = find_col(df, ['MONTH', 'DATE'])
    prod_col = find_col(df, ['PRODUCTION'])
    rej_pct_col = find_col(df, ['REJ %', 'REJ%', 'REJECTION %'])
    
    # Fallback to positional
    if sno_col is None:
        sno_col = df.columns[0]
    if month_col is None:
        month_col = df.columns[1]
    if prod_col is None:
        prod_col = df.columns[2]
    if rej_pct_col is None:
        rej_pct_col = df.columns[5]
    
    # Filter rows with valid data
    df = df[pd.to_numeric(df[sno_col], errors='coerce').notna()]
    df = df[pd.to_numeric(df[prod_col], errors='coerce').notna()]
    
    # Build result DataFrame
    result = pd.DataFrame()
    
    # Convert MONTH dates to readable format (Apr-25, May-25, etc.)
    def format_month(dt):
        if pd.isna(dt):
            return None
        if isinstance(dt, datetime):
            return dt.strftime('%b-%y')
        return str(dt)
    
    result['Month'] = df[month_col].apply(format_month)
    result['Production_Qty'] = pd.to_numeric(df[prod_col], errors='coerce').fillna(0)
    result['Rejection_Rate'] = pd.to_numeric(df[rej_pct_col], errors='coerce').fillna(0)
    
    # Clean and convert types
    result = result[result['Month'].notna()]
    result['Month'] = result['Month'].astype(str)
    result = result.reset_index(drop=True)
    
    return result


def load_visual_defects(file_buffer) -> pd.DataFrame:
    """
    Loads Visual Inspection Defects (Pareto Data) from uploaded file.
    Source: VISUAL INSPECTION REPORT 2025.xlsx
    """
    if file_buffer is None:
        return pd.DataFrame({'Defect': [], 'Quantity': []})
    
    xl = pd.ExcelFile(file_buffer)
    
    # Defect code mappings
    defect_names = {
        'COAG': 'Coagulum (COAG)',
        'SD': 'Surface Defect (SD)',
        'PS': 'Pin Hole (PS)',
        'BM': 'Black Mark (BM)',
        'RW': 'Raised Wire (RW)',
        'BEP': 'Beading Problem (BEP)',
        'WK': 'Wrinkle (WK)',
        'TF': 'Touching (TF)',
        'BMP': 'Black Mark Print (BMP)',
        'TT': 'Tearing (TT)',
        'BL': 'Bloated (BL)',
        'SB': 'Stain/Blemish (SB)',
        'PW': 'Pin Wire (PW)',
        'FP': 'Foreign Particle (FP)',
        'DEC': 'Decoloration (DEC)',
        'WEB': 'Webbing (WEB)',
        'BT': 'Butterfly (BT)',
        'SF': 'Surface Flaw (SF)',
        'BIC': 'Bicone (BIC)',
        'PH': 'Pin Hole (PH)',
        'BST': 'Burst (BST)'
    }
    
    defect_totals = {}
    
    monthly_sheets = [s for s in xl.sheet_names if any(m in s.upper() for m in ['APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'JANUARY'])]
    
    for sheet in monthly_sheets:
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=None)
            
            code_row = None
            for i, row in df.iterrows():
                row_str = ' '.join([str(x) for x in row.values if pd.notna(x)])
                if 'COAG' in row_str and 'SD' in row_str:
                    code_row = i
                    break
            
            if code_row is not None:
                codes = df.iloc[code_row].values
                data_df = df.iloc[code_row+1:].copy()
                
                for col_idx, code in enumerate(codes):
                    if pd.notna(code) and str(code) in defect_names:
                        col_sum = pd.to_numeric(data_df.iloc[:, col_idx], errors='coerce').sum()
                        defect_totals[str(code)] = defect_totals.get(str(code), 0) + col_sum
        except:
            continue
    
    result_data = []
    for code, total in defect_totals.items():
        if total > 0:
            name = defect_names.get(code, code)
            result_data.append({'Defect': name, 'Quantity': total})
    
    if not result_data:
        result_data = [{'Defect': 'No data', 'Quantity': 0}]
    
    result = pd.DataFrame(result_data)
    result['Quantity'] = pd.to_numeric(result['Quantity'], errors='coerce').fillna(0)
    result = result[result['Quantity'] > 0] if len(result[result['Quantity'] > 0]) > 0 else result
    result = result.sort_values(by='Quantity', ascending=False).head(10)
    result['Defect'] = result['Defect'].astype(str)
    result = result.reset_index(drop=True)
    
    return result


def load_shop_floor_defects(file_buffer) -> pd.DataFrame:
    """
    Loads Shop Floor (Dipping) Defects from uploaded file.
    Source: SHOPFLOOR REJECTION REPORT.xlsx
    """
    if file_buffer is None:
        return pd.DataFrame({'Defect': [], 'Quantity': []})
    
    xl = pd.ExcelFile(file_buffer)
    
    defect_columns = ['COAG', 'Raised Wire', 'Surface Defect', 'Overlaping', 'Black Mark', 'Webbing', 'Missing Formers', 'Others']
    defect_totals = {col: 0 for col in defect_columns}
    
    monthly_sheets = [s for s in xl.sheet_names if any(m in s.upper() for m in ['APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'JANUARY'])]
    
    for sheet in monthly_sheets:
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=2)
            
            for col in defect_columns:
                for df_col in df.columns:
                    if col.lower() in str(df_col).lower():
                        col_sum = pd.to_numeric(df[df_col], errors='coerce').sum()
                        defect_totals[col] += col_sum
                        break
        except:
            continue
    
    result_data = []
    for defect, total in defect_totals.items():
        if total > 0:
            result_data.append({'Defect': defect, 'Quantity': total})
    
    if not result_data:
        result_data = [{'Defect': 'No data', 'Quantity': 0}]
    
    result = pd.DataFrame(result_data)
    result['Quantity'] = pd.to_numeric(result['Quantity'], errors='coerce').fillna(0)
    result = result[result['Quantity'] > 0] if len(result[result['Quantity'] > 0]) > 0 else result
    result = result.sort_values(by='Quantity', ascending=False).head(10)
    result['Defect'] = result['Defect'].astype(str)
    result = result.reset_index(drop=True)
    
    return result


def load_integrity_data(file_buffer) -> pd.DataFrame:
    """
    Loads Balloon & Valve Integrity Inspection Data from uploaded file.
    Source: BALLOON & VALVE INTEGRITY INSPECTION REPORT FILE 2025.xlsx
    """
    if file_buffer is None:
        return pd.DataFrame({'Test_Type': [], 'Defect_Type': [], 'Quantity': []})
    
    xl = pd.ExcelFile(file_buffer)
    
    balloon_defects = {'STRUCK BALLOON': 0, 'BALLOON BURST': 0, 'LEAKAGE': 0}
    valve_defects = {'THIN SPOT': 0, 'LEAKAGE': 0, '90/10': 0}
    
    monthly_sheets = [s for s in xl.sheet_names if any(m in s.upper() for m in ['APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER', 'JANUARY'])]
    
    for sheet in monthly_sheets:
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=None)
            
            header_row = None
            for i, row in df.iterrows():
                row_str = ' '.join([str(x) for x in row.values if pd.notna(x)]).upper()
                if 'STRUCK BALLOON' in row_str or 'CHECKED QTY' in row_str:
                    header_row = i
                    break
            
            if header_row is not None:
                headers = df.iloc[header_row].values
                data_df = df.iloc[header_row+1:]
                
                for col_idx, header in enumerate(headers):
                    if pd.isna(header):
                        continue
                    header_str = str(header).upper()
                    
                    if 'STRUCK' in header_str:
                        balloon_defects['STRUCK BALLOON'] += pd.to_numeric(data_df.iloc[:, col_idx], errors='coerce').sum()
                    elif 'BRUST' in header_str or 'BURST' in header_str:
                        balloon_defects['BALLOON BURST'] += pd.to_numeric(data_df.iloc[:, col_idx], errors='coerce').sum()
                    
                    if 'THIN' in header_str:
                        valve_defects['THIN SPOT'] += pd.to_numeric(data_df.iloc[:, col_idx], errors='coerce').sum()
                    elif '90/10' in header_str or '90' in header_str:
                        valve_defects['90/10'] += pd.to_numeric(data_df.iloc[:, col_idx], errors='coerce').sum()
        except:
            continue
    
    result_data = []
    
    for defect, qty in balloon_defects.items():
        if qty > 0:
            result_data.append({
                'Test_Type': 'Balloon Integrity',
                'Defect_Type': defect.title(),
                'Quantity': qty
            })
    
    for defect, qty in valve_defects.items():
        if qty > 0:
            result_data.append({
                'Test_Type': 'Valve Integrity',
                'Defect_Type': defect.title() if defect != '90/10' else '90/10 Defect',
                'Quantity': qty
            })
    
    if not result_data:
        result_data = [
            {'Test_Type': 'No data', 'Defect_Type': 'Upload file', 'Quantity': 0}
        ]
    
    result = pd.DataFrame(result_data)
    result['Quantity'] = pd.to_numeric(result['Quantity'], errors='coerce').fillna(0)
    result['Test_Type'] = result['Test_Type'].astype(str)
    result['Defect_Type'] = result['Defect_Type'].astype(str)
    result = result.reset_index(drop=True)
    
    return result


def load_assembly_rejection(file_buffer) -> pd.DataFrame:
    """
    Loads Assembly Rejection Report data from uploaded file.
    Source: ASSEMBLY REJECTION REPORT.xlsx
    Contains daily rejection data for Visual, Balloon, and Valve testing.
    """
    if file_buffer is None:
        return pd.DataFrame({'Month': [], 'Visual_Rej': [], 'Balloon_Rej': [], 
                            'Valve_Rej': [], 'Total_Rej': []})
    
    xl = pd.ExcelFile(file_buffer)
    
    monthly_data = []
    month_names = {
        'APRIL': 'Apr-25', 'MAY': 'May-25', 'JUNE': 'Jun-25', 
        'JULY': 'Jul-25', 'AUGUST': 'Aug-25', 'SEPTEMBER': 'Sep-25',
        'OCTOBER': 'Oct-25', 'NOVEMBER': 'Nov-25', 'DECEMBER': 'Dec-25',
        'JANUARY': 'Jan-26'
    }
    
    for sheet in xl.sheet_names:
        # Find month name
        month_key = None
        for m in month_names.keys():
            if m in sheet.upper():
                month_key = m
                break
        
        if month_key is None:
            continue
        
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=None)
            
            # Find header row (contains DATE, VISUAL\nQTY, etc.)
            header_row = None
            for i, row in df.iterrows():
                row_str = ' '.join([str(x) for x in row.values if pd.notna(x)]).upper()
                if 'DATE' in row_str and 'VISUAL' in row_str:
                    header_row = i
                    break
            
            if header_row is None:
                continue
            
            headers = df.iloc[header_row].values
            data_df = df.iloc[header_row+1:]
            
            # Find column indices
            visual_rej_idx = None
            balloon_rej_idx = None
            valve_rej_idx = None
            total_rej_idx = None
            
            for idx, h in enumerate(headers):
                if pd.isna(h):
                    continue
                h_str = str(h).upper().replace('\n', ' ')
                
                # Visual rejection column (first REJ QTY)
                if visual_rej_idx is None and 'REJ' in h_str and 'QTY' in h_str:
                    visual_rej_idx = idx
                # Look for balloon and valve rej columns by position relative to balloon/valve checked qty
                if 'BALLOON' in h_str and 'CHKD' in h_str:
                    balloon_rej_idx = idx + 2  # REJ QTY is 2 columns after CHKD QTY
                if 'VALVE' in h_str and 'CHKD' in h_str:
                    valve_rej_idx = idx + 2
                if 'TOTAL REJ' in h_str:
                    total_rej_idx = idx
            
            # Sum up monthly data
            visual_rej = 0
            balloon_rej = 0
            valve_rej = 0
            total_rej = 0
            
            for _, row in data_df.iterrows():
                # Skip summary rows (where DATE is NaN or contains 'SUNDAY')
                date_val = row.iloc[0]
                if pd.isna(date_val) or 'SUNDAY' in str(date_val).upper():
                    continue
                
                if visual_rej_idx is not None:
                    val = pd.to_numeric(row.iloc[visual_rej_idx], errors='coerce')
                    if not pd.isna(val):
                        visual_rej += val
                
                if balloon_rej_idx is not None and balloon_rej_idx < len(row):
                    val = pd.to_numeric(row.iloc[balloon_rej_idx], errors='coerce')
                    if not pd.isna(val):
                        balloon_rej += val
                
                if valve_rej_idx is not None and valve_rej_idx < len(row):
                    val = pd.to_numeric(row.iloc[valve_rej_idx], errors='coerce')
                    if not pd.isna(val):
                        valve_rej += val
                
                if total_rej_idx is not None:
                    val = pd.to_numeric(row.iloc[total_rej_idx], errors='coerce')
                    if not pd.isna(val):
                        total_rej += val
            
            monthly_data.append({
                'Month': month_names[month_key],
                'Visual_Rej': visual_rej,
                'Balloon_Rej': balloon_rej,
                'Valve_Rej': valve_rej,
                'Total_Rej': total_rej
            })
            
        except Exception as e:
            continue
    
    if not monthly_data:
        monthly_data = [{'Month': 'No data', 'Visual_Rej': 0, 'Balloon_Rej': 0, 
                        'Valve_Rej': 0, 'Total_Rej': 0}]
    
    result = pd.DataFrame(monthly_data)
    result['Month'] = result['Month'].astype(str)
    result = result.reset_index(drop=True)
    
    return result
