# normalizer.py
import json
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── пресеты (пример) ───────────────────────────────────────────
CI_VALUES = {"La": 0.237, "Ce": 0.613, "Pr": 0.092, "Nd": 0.457}
PM_VALUES = {"La": 0.28 , "Ce": 0.73 , "Pr": 0.108, "Nd": 0.57 }

_PRESETS = {
    "— choose —": None,
    "CI Chondrite"     : CI_VALUES,
    "Primitive Mantle" : PM_VALUES,
}


# Список всех химических элементов для проверки
CHEMICAL_ELEMENTS = {
    'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
    'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
    'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
    'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
    'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn',
    'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr',
    'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og'
}


def normalize_column_names(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """
    Нормализует названия столбцов, извлекая символы химических элементов.
    
    Примеры преобразований:
    - "CE_PPM" → "Ce"
    - "la_ppm" → "La"  
    - "Nd_wt%" → "Nd"
    - "PR-CONC" → "Pr"
    - "Ce" → "Ce" (уже правильно)
    
    Args:
        df: исходный DataFrame
        
    Returns:
        tuple: (новый DataFrame с переименованными столбцами, словарь маппинга старое_имя → новое_имя)
    """
    
    mapping = {}
    new_columns = []
    
    for col in df.columns:
        # Проверяем, является ли столбец числовым
        if not pd.api.types.is_numeric_dtype(df[col]):
            new_columns.append(col)  # Нечисловые столбцы оставляем как есть
            continue
            
        # Ищем химический элемент в названии столбца
        element = extract_element_from_column(col)
        
        if element:
            mapping[col] = element
            new_columns.append(element)
        else:
            new_columns.append(col)  # Если элемент не найден, оставляем как есть
    
    # Создаем новый DataFrame с переименованными столбцами
    df_normalized = df.copy()
    df_normalized.columns = new_columns
    
    return df_normalized, mapping

def extract_element_from_column(col_name: str) -> str | None:
    """
    Извлекает символ химического элемента из названия столбца.
    ТОЛЬКО для очевидных паттернов (элемент_единица, элемент-единица, элемент_концентрация)
    
    Args:
        col_name: название столбца
        
    Returns:
        символ элемента в правильном регистре или None, если не найден
    """
    
    # Проверяем, не является ли это оксидом
    if is_oxide_column(col_name):
        return None
    
    # Проверяем, не является ли это служебным столбцом
    if is_service_column(col_name):
        return None
    
    # Элементы из ваших словарей нормировки
    TARGET_ELEMENTS = set(CI_VALUES.keys()) | set(PM_VALUES.keys())
    
    # ТОЛЬКО очевидные паттерны для переименования
    obvious_patterns = [
        r'^([A-Za-z]{1,2})_PPM',           # Ce_PPM, LA_PPM
        r'^([A-Za-z]{1,2})_ppm',           # Ce_ppm, la_ppm
        r'^([A-Za-z]{1,2})_WT',            # Ce_WT, la_wt
        r'^([A-Za-z]{1,2})_wt',            # Ce_wt, la_wt
        r'^([A-Za-z]{1,2})_CONC',          # Ce_CONC, la_conc
        r'^([A-Za-z]{1,2})_conc',          # Ce_conc, la_conc
        r'^([A-Za-z]{1,2})_CONTENT',       # Ce_CONTENT
        r'^([A-Za-z]{1,2})_content',       # Ce_content
        r'^([A-Za-z]{1,2})-PPM',           # Ce-PPM, LA-PPM
        r'^([A-Za-z]{1,2})-ppm',           # Ce-ppm, la-ppm
        r'^([A-Za-z]{1,2})-WT',            # Ce-WT, la-wt
        r'^([A-Za-z]{1,2})-wt',            # Ce-wt, la-wt
        r'^([A-Za-z]{1,2})-CONC',          # Ce-CONC, la-conc
        r'^([A-Za-z]{1,2})-conc',          # Ce-conc, la-conc
        r'^([A-Za-z]{1,2})_UG_G',          # Ce_UG_G (микрограмм на грамм)
        r'^([A-Za-z]{1,2})_ug_g',          # Ce_ug_g
        r'^([A-Za-z]{1,2})_MG_KG',         # Ce_MG_KG (миллиграмм на килограмм)
        r'^([A-Za-z]{1,2})_mg_kg',         # Ce_mg_kg
    ]
    
    for pattern in obvious_patterns:
        match = re.match(pattern, col_name, re.IGNORECASE)
        if match:
            element = match.group(1).capitalize()
            
            # Проверяем, что это элемент из наших словарей нормировки
            if element in TARGET_ELEMENTS:
                return element
    
    return None

def show_column_mapping(mapping: dict[str, str]):
    """
    Показывает таблицу маппинга столбцов в Streamlit.
    
    Args:
        mapping: словарь маппинга старое_имя → новое_имя
    """
    if mapping:
        st.write("**Переименованные столбцы:**")
        mapping_df = pd.DataFrame(
            [(old, new) for old, new in mapping.items()],
            columns=["Исходное название", "Новое название"]
        )
        st.dataframe(mapping_df, use_container_width=True)

# Пример использования:
def process_uploaded_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Обрабатывает загруженные данные, нормализуя названия столбцов.
    
    Args:
        df: исходный DataFrame
        
    Returns:
        DataFrame с нормализованными названиями столбцов
    """
    
    # Нормализуем названия столбцов
    df_normalized, mapping = normalize_column_names(df)
    
    # Показываем пользователю, что было изменено
    if mapping:
        show_column_mapping(mapping)
        st.success(f"Переименовано столбцов: {len(mapping)}")
    
    return df_normalized


def is_oxide_column(col_name: str) -> bool:
    """
    Проверяет, является ли столбец оксидом (K2O, TiO2, SiO2 и т.д.)
    
    Args:
        col_name: название столбца
        
    Returns:
        True, если это оксид
    """
    # Убираем лишние символы и приводим к верхнему регистру
    clean_name = re.sub(r'[_\-\s]', '', col_name).upper()
    
    # Паттерны для оксидов
    oxide_patterns = [
        r'^[A-Z]+\d*O\d*$',      # K2O, TiO2, SiO2, Al2O3, Fe2O3
        r'^[A-Z]+O\d*$',         # CaO, MgO, Na2O
        r'O\d*$',                # Заканчивается на O + цифры
        r'\d+O\d*',              # Содержит цифры + O + цифры
    ]
    
    for pattern in oxide_patterns:
        if re.search(pattern, clean_name):
            return True
    
    return False


def is_service_column(col_name: str) -> bool:
    """
    Проверяет, является ли столбец служебным (TOTAL, SUM, AVERAGE и т.д.)
    
    Args:
        col_name: название столбца
        
    Returns:
        True, если это служебный столбец
    """
    # Убираем лишние символы и приводим к верхнему регистру
    clean_name = re.sub(r'[_\-\s]', '', col_name).upper()
    
    # Список служебных названий
    service_names = {
        'TOTAL', 'SUM', 'AVERAGE', 'AVG', 'MEAN', 'MEDIAN', 
        'COUNT', 'MIN', 'MAX', 'STD', 'VARIANCE', 'VAR',
        'INDEX', 'ID', 'SAMPLE', 'NAME', 'NUMBER', 'NUM',
        'DATE', 'TIME', 'LOCATION', 'LOC', 'DEPTH', 'LEVEL'
    }
    
    # Проверяем точное совпадение
    if clean_name in service_names:
        return True
    
    # Проверяем, начинается ли с служебного слова
    for service in service_names:
        if clean_name.startswith(service):
            return True
    
    return False















# ── 1. UI-контроль: выбор элементов и нормировки ───────────────
def norm_controls(df: pd.DataFrame):
    """Возвращает (ordered_elems, norm_dict) или (None, None)."""
    st.sidebar.markdown("## Normalized spider-plot")

    # динамический список элементов
    if "elem_list" not in st.session_state:
        st.session_state.elem_list = [""]

    elem_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    remove = []
    for i, val in enumerate(st.session_state.elem_list):
        cols = st.sidebar.columns([5, 1])
        choice = cols[0].selectbox(
            f"{i+1}", [""] + elem_cols,
            index=([""] + elem_cols).index(val) if val in elem_cols else 0,
            key=f"elem_sel_{i}"
        )
        st.session_state.elem_list[i] = choice
        if cols[1].button("✖", key=f"elem_del_{i}"):
            remove.append(i)

    for idx in sorted(remove, reverse=True):
        st.session_state.elem_list.pop(idx)

    if st.sidebar.button("➕  Add element"):
        st.session_state.elem_list.append("")

    ordered_elems = [e for e in st.session_state.elem_list if e]

    # выбор норм-набора
    st.sidebar.markdown("### Normalization set")
    preset_name = st.sidebar.selectbox("Preset", list(_PRESETS.keys()), index=0)
    uploaded = st.sidebar.file_uploader("…or upload JSON {elem: value}", type=["json"])

    if uploaded:
        norm_dict = json.load(uploaded)
    else:
        norm_dict = _PRESETS[preset_name]

    if not ordered_elems or norm_dict is None:
        return None, None

    st.sidebar.download_button(
        "💾 Save current norm", data=json.dumps(norm_dict, indent=2).encode(),
        file_name="norm_set.json", mime="application/json",
        use_container_width=True,
    )
    return ordered_elems, norm_dict


def multielemental_plot(
    df: pd.DataFrame, elems: list[str], norm_dict: dict[str, float],
    group_col: str | None = None,
    color_map: dict | None = None,          # цвет маркеров
    symbol_map: dict | None = None,
    size_map: dict | None = None,
    width_map: dict | None = None,          # толщина линии
    dash_map: dict | None = None,           # стиль штриха
    line_color_map: dict | None = None,     # цвет линии
    outline_color_map: dict | None = None,  # цвет обводки маркера
    outline_width_map: dict | None = None,  # толщина обводки маркера
    hover_cols: list[str] | None = None,    # колонки для всплывающих подсказок
    log_y: bool = True,
):
    # ── нормировка ─────────────────────────────────────────────
    df_vals = df[elems].dropna()
    normed  = df_vals.apply(lambda c: c / norm_dict.get(c.name, 1), axis=0)

    fig = go.Figure()
    first_seen = set()


    for idx, row in normed.iterrows():
        grp = df.loc[idx, group_col] if group_col else "All"

        show_flag = grp not in first_seen     # ← запомнили флаг

        # ── стили текущей группы ───────────────────────────────
        m_color = color_map.get(grp, "#1f77b4")  if color_map else "#1f77b4"
        l_color = line_color_map.get(grp, m_color) if line_color_map else m_color

        marker_sym = symbol_map.get(grp, "circle") if symbol_map else "circle"
        marker_sz  = size_map.get(grp, 6)          if size_map  else 6

        line_wid   = width_map.get(grp, 2)         if width_map else 2
        line_dash  = dash_map.get(grp, "solid")    if dash_map else "solid"

        out_color  = outline_color_map.get(grp, "#000000") if outline_color_map else "#000000"
        out_width  = outline_width_map.get(grp, 0)         if outline_width_map else 0

        # ── добавляем линию+маркеры ────────────────────────────
        fig.add_trace(go.Scatter(
            x=elems,
            y=row.values,
            mode="lines+markers",
            name=str(grp),
            legendgroup=str(grp),
            showlegend=show_flag,
            line=dict(color=l_color, width=line_wid, dash=line_dash),
            marker=dict(
                color=m_color,
                symbol=marker_sym,
                size=marker_sz,
                line=dict(color=out_color, width=out_width)
            ),
            hovertemplate="<b>%{x}</b><br>Norm=%{y:.3g}<extra></extra>"
        ))
        if show_flag:
            first_seen.add(grp)


    fig.update_xaxes(
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )

    fig.update_yaxes(
        title_text="Value / Norm",
        title_font=dict(size=18, color="#111111"),
        tickfont=dict(size=14, color="#111111"),    # <--- ВАЖНО!
        linecolor="#000000", mirror=True, showline=True,
        ticks="inside", ticklen=6, tickwidth=1, tickcolor="#000000",
        gridcolor="rgba(0,0,0,0.15)",
        minor_showgrid=True, minor_gridwidth=0.5,
        minor_gridcolor="rgba(0,0,0,0.05)",
    )

    fig.update_layout(
    xaxis=dict(title="Elements", type="category"),
    yaxis=dict(title="Value / Norm",
               type="log" if log_y else "linear"),
    hovermode="x unified",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    height=650, width=800,
    showlegend=True,
    legend_title=group_col if group_col else "",
    legend=dict(                       # ─── НОВОЕ ───
        font=dict(size=14, color="#111111"),
        bgcolor="rgba(255,255,255,0.8)",   # слегка прозрачный фон
        bordercolor="#000000",
        borderwidth=1
    )
)
    return fig

