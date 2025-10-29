import pandas as pd

# ===== Fungsi Load CSV Aman =====
def load_csv(path, numeric_cols=[]):
    df = pd.read_csv(path)
    for col in numeric_cols:
        df[col] = df[col].fillna(0).astype(str).str.replace('.', '').str.replace('W','').replace('', '0').astype(int)
    return df

# ===== Fungsi Pilih Komponen =====
def select_component(df, max_price, allow_over=False):
    candidates = df[df['price_idr'] <= max_price]
    if len(candidates) == 0:
        if allow_over:
            # ambil yang paling murah meskipun melebihi alokasi budget
            return df.loc[df['price_idr'].idxmin()], True
        return None, False
    return candidates.loc[candidates['price_idr'].idxmax()], False

# ===== Load Dataset =====
cpu_df = load_csv("data/cpu.csv", numeric_cols=['price_idr', 'tdp'])
gpu_df = load_csv("data/gpu.csv", numeric_cols=['price_idr', 'tdp', 'length_mm'])
mb_df = load_csv("data/motherboard.csv", numeric_cols=['price_idr'])
ram_df = load_csv("data/ram.csv", numeric_cols=['price_idr'])
storage_df = load_csv("data/storage.csv", numeric_cols=['price_idr'])
psu_df = load_csv("data/psu.csv", numeric_cols=['price_idr', 'power'])
case_df = load_csv("data/case.csv", numeric_cols=['price_idr', 'gpu_max_length_mm'])
cooling_df = load_csv("data/cooling.csv", numeric_cols=['price_idr'])

# ===== Fungsi Utama Rekomendasi PC =====
def recommend_pc(budget):
    notes = []

    # ===== Tentukan Level Build =====
    if budget < 20000000:
        level = 'entry-level'
    elif budget < 50000000:
        level = 'mid-range'
    else:
        level = 'high-end'

    # ===== Alokasi Budget (%) =====
    allocation = {
        'cpu': 0.30,
        'gpu': 0.25,
        'motherboard': 0.10,
        'ram': 0.10,
        'storage': 0.08,
        'psu': 0.08,
        'case': 0.07,
        'cooling': 0.02
    }

    # ===== Pilih CPU =====
    cpu_budget = int(budget * allocation['cpu'])
    cpu, over = select_component(cpu_df, cpu_budget, allow_over=True)
    if over:
        notes.append("CPU melebihi alokasi budget")
    budget -= cpu['price_idr']

    # ===== Pilih Motherboard =====
    mb_budget = int(budget * allocation['motherboard'])
    mb_candidates = mb_df[mb_df['socket'] == cpu['socket']]
    motherboard, over = select_component(mb_candidates, mb_budget, allow_over=True)
    if over:
        notes.append("Motherboard melebihi alokasi budget")
    budget -= motherboard['price_idr']

    # ===== Pilih RAM =====
    ram_budget = int(budget * allocation['ram'])
    ram, over = select_component(ram_df, ram_budget, allow_over=True)
    if over:
        notes.append("RAM melebihi alokasi budget")
    budget -= ram['price_idr']

    # ===== Pilih Storage =====
    storage_budget = int(budget * allocation['storage'])
    storage, over = select_component(storage_df, storage_budget, allow_over=True)
    if over:
        notes.append("Storage melebihi alokasi budget")
    budget -= storage['price_idr']

    # ===== Pilih Case =====
    case_budget = int(budget * allocation['case'])
    case, over = select_component(case_df, case_budget, allow_over=True)
    if over:
        notes.append("Case melebihi alokasi budget")
    budget -= case['price_idr']

    # ===== Pilih GPU =====
    gpu_budget = int(budget * allocation['gpu'])
    gpu_candidates = gpu_df[gpu_df['length_mm'] <= case['gpu_max_length_mm']]
    gpu, over = select_component(gpu_candidates, gpu_budget, allow_over=True)
    if over:
        notes.append("GPU melebihi alokasi budget atau panjang melebihi case")
    budget -= gpu['price_idr']

    # ===== Pilih PSU =====
    total_tdp = cpu['tdp'] + gpu['tdp']
    psu_budget = int(budget * allocation['psu'])
    psu_candidates = psu_df[psu_df['power'] >= total_tdp]
    psu, over = select_component(psu_candidates, psu_budget, allow_over=True)
    if over:
        notes.append("PSU melebihi alokasi budget atau kurang daya")
    budget -= psu['price_idr']

    # ===== Pilih Cooling =====
    cooling_budget = int(budget * allocation['cooling'])
    cooling, over = select_component(cooling_df, cooling_budget, allow_over=True)
    if over:
        notes.append("Cooling melebihi alokasi budget")

    # ===== Total Harga =====
    total_price = (cpu['price_idr'] + motherboard['price_idr'] + ram['price_idr'] +
                   storage['price_idr'] + case['price_idr'] + gpu['price_idr'] +
                   psu['price_idr'] + cooling['price_idr'])

    # ===== Build Dictionary =====
    build = {
        'cpu': cpu,
        'motherboard': motherboard,
        'ram': ram,
        'storage': storage,
        'case': case,
        'gpu': gpu,
        'psu': psu,
        'cooling': cooling,
        'notes': notes
    }

    return build, total_price
