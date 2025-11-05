import pandas as pd

# ===== DATABASE TDP & COOLING CAPACITY =====
CPU_TDP_MAX = {
    'Core i5-12400F': 117,
    'Core i5-12600K': 150,
    'Core i7-12700K': 190,
    'Core i7-13700K': 253,
    'Core i9-13900K': 253,
    'Core i9-14900K': 253,
    'Ryzen 5 5600X': 88,
    'Ryzen 7 5800X': 142,
    'Ryzen 7 7800X3D': 162,
    'Ryzen 9 7900X': 230,
    'Ryzen 9 7950X': 230,
}

COOLING_CAPACITY = {
    'GAMMAXX 400 Pro': 150,
    'Hyper 212 Black Edition': 180,
    'Pure Rock 2': 150,
    'NH-U12S Redux': 200,
    'LS520 240mm': 250,
    'iCUE H100i Elite Capellix': 280,
    'Kraken X63': 300,
    'Galahad 360': 350,
    'Ryujin II 360': 400,
    'iCUE H150i Elite LCD': 380,
}

# ===== CPU GENERATION & CHIPSET COMPATIBILITY =====
CHIPSET_COMPATIBILITY = {
    # Intel Gen 12
    'LGA1700_GEN12': {
        'cpus': ['Core i5-12400F', 'Core i5-12600K', 'Core i7-12700K'],
        'chipsets': ['B660', 'H610', 'Z690']
    },
    # Intel Gen 13
    'LGA1700_GEN13': {
        'cpus': ['Core i5-13400F', 'Core i7-13700K', 'Core i9-13900K'],
        'chipsets': ['B760', 'H770', 'Z790']
    },
    # Intel Gen 14
    'LGA1700_GEN14': {
        'cpus': ['Core i5-14400F', 'Core i9-14900K'],
        'chipsets': ['B760', 'H770', 'Z790']
    },
    # AMD Ryzen 5000
    'AM4': {
        'cpus': ['Ryzen 5 5600X', 'Ryzen 7 5800X'],
        'chipsets': ['A520', 'B550', 'X570']
    },
    # AMD Ryzen 7000
    'AM5': {
        'cpus': ['Ryzen 7 7800X3D', 'Ryzen 9 7900X', 'Ryzen 9 7950X'],
        'chipsets': ['A620', 'B650', 'B650E', 'X670', 'X670E']
    }
}

# ===== K-SERIES CPU RECOMMENDATIONS =====
K_SERIES_CHIPSETS = ['Z690', 'Z790']

# ===== Fungsi Load CSV Aman =====
def load_csv(path, numeric_cols=[]):
    df = pd.read_csv(path)
    for col in numeric_cols:
        df[col] = df[col].fillna(0).astype(str).str.replace('.', '').replace('', '0').astype(int)
    return df

# ===== Load Dataset =====
cpu_df = load_csv("data/cpu.csv", numeric_cols=['price_idr', 'tdp'])
gpu_df = load_csv("data/gpu.csv", numeric_cols=['price_idr', 'tdp', 'length_mm'])
mb_df = load_csv("data/motherboard.csv", numeric_cols=['price_idr'])
ram_df = load_csv("data/ram.csv", numeric_cols=['price_idr'])
storage_df = load_csv("data/storage.csv", numeric_cols=['price_idr'])
psu_df = load_csv("data/psu.csv", numeric_cols=['price_idr', 'power'])
case_df = load_csv("data/case.csv", numeric_cols=['price_idr', 'gpu_max_length_mm'])
cooling_df = load_csv("data/cooling.csv", numeric_cols=['price_idr'])

# ===== VALIDASI FUNCTIONS =====

def validate_cpu_chipset(cpu_model, chipset):
    """Validasi apakah CPU generation cocok dengan chipset motherboard"""
    for compat_group, info in CHIPSET_COMPATIBILITY.items():
        if cpu_model in info['cpus']:
            if any(cs in chipset for cs in info['chipsets']):
                return True, ""
            else:
                return False, f"CPU {cpu_model} tidak kompatibel dengan chipset {chipset}. Gunakan chipset: {', '.join(info['chipsets'])}"
    return True, ""  # Default pass jika tidak ada di database

def validate_ram_type(cpu_model, motherboard_ram_type, ram_type):
    """Validasi apakah tipe RAM (DDR4/DDR5) cocok dengan CPU & Motherboard"""
    # Ryzen 7000 HANYA DDR5
    if 'Ryzen' in cpu_model and ' 7' in cpu_model:
        if ram_type != 'DDR5':
            return False, f"CPU {cpu_model} (Ryzen 7000) HANYA mendukung DDR5, bukan {ram_type}"
    
    # Cek motherboard RAM type
    if motherboard_ram_type != ram_type:
        return False, f"Motherboard mendukung {motherboard_ram_type}, tetapi RAM yang dipilih adalah {ram_type}"
    
    return True, ""

def validate_cooling_capacity(cpu_model, cooling_model):
    """Validasi apakah cooling cukup untuk CPU"""
    cpu_max_tdp = CPU_TDP_MAX.get(cpu_model, 125)  # Default 125W
    cooling_cap = COOLING_CAPACITY.get(cooling_model, 100)  # Default 100W
    
    if cooling_cap < cpu_max_tdp:
        return False, f"Cooling tidak cukup! CPU max {cpu_max_tdp}W, cooler hanya {cooling_cap}W. CPU akan overheat!"
    
    # Warning jika margin terlalu kecil (<20%)
    margin = ((cooling_cap - cpu_max_tdp) / cpu_max_tdp) * 100
    if margin < 20:
        return True, f"⚠️ Cooling capacity margin tipis ({margin:.0f}%). Pertimbangkan cooler lebih kuat."
    
    return True, ""

def validate_psu_wattage(cpu_tdp, gpu_tdp, psu_power):
    """Validasi apakah PSU cukup dengan formula yang benar"""
    # Formula: (CPU max + GPU) * 1.5 + 100W headroom
    cpu_max = CPU_TDP_MAX.get(cpu_tdp, cpu_tdp)  # Ambil max TDP
    required_wattage = int((cpu_max + gpu_tdp) * 1.5 + 100)
    
    if psu_power < required_wattage:
        return False, f"PSU tidak cukup! Dibutuhkan minimum {required_wattage}W, PSU hanya {psu_power}W"
    
    return True, ""

def validate_k_series_chipset(cpu_model, chipset):
    """Validasi K-series CPU dengan chipset yang tepat"""
    if cpu_model.endswith('K'):
        if not any(z_chip in chipset for z_chip in K_SERIES_CHIPSETS):
            return False, f"CPU {cpu_model} adalah K-series (unlocked) tetapi motherboard {chipset} tidak bisa overclock. Gunakan Z690/Z790 atau pilih CPU non-K untuk menghemat."
    return True, ""

# ===== DYNAMIC BUDGET ALLOCATION =====
def get_budget_allocation(total_budget):
    """Alokasi budget dinamis berdasarkan total budget"""
    if total_budget < 10_000_000:
        # Budget rendah: prioritas CPU & GPU seimbang
        return {
            'cpu': 0.25,
            'gpu': 0.30,
            'motherboard': 0.15,
            'ram': 0.10,
            'storage': 0.08,
            'psu': 0.06,
            'case': 0.04,
            'cooling': 0.02
        }
    elif total_budget < 20_000_000:
        # Budget menengah: GPU lebih prioritas
        return {
            'cpu': 0.25,
            'gpu': 0.35,
            'motherboard': 0.13,
            'ram': 0.10,
            'storage': 0.07,
            'psu': 0.05,
            'case': 0.03,
            'cooling': 0.02
        }
    elif total_budget < 30_000_000:
        # Budget tinggi: GPU dominan untuk gaming
        return {
            'cpu': 0.22,
            'gpu': 0.40,
            'motherboard': 0.12,
            'ram': 0.10,
            'storage': 0.06,
            'psu': 0.05,
            'case': 0.03,
            'cooling': 0.02
        }
    else:
        # Budget sangat tinggi: GPU ultra prioritas
        return {
            'cpu': 0.20,
            'gpu': 0.45,
            'motherboard': 0.10,
            'ram': 0.08,
            'storage': 0.07,
            'psu': 0.05,
            'case': 0.03,
            'cooling': 0.02
        }

# ===== Fungsi Pilih Komponen =====
def select_component(df, max_price, allow_over=False):
    candidates = df[df['price_idr'] <= max_price]
    if len(candidates) == 0:
        if allow_over:
            return df.loc[df['price_idr'].idxmin()], True
        return None, False
    return candidates.loc[candidates['price_idr'].idxmax()], False

# ===== Fungsi Utama Rekomendasi PC =====
def recommend_pc(budget):
    errors = []
    warnings = []
    notes = []
    original_budget = budget

    # ===== Alokasi Budget Dinamis =====
    allocation = get_budget_allocation(budget)

    # ===== Pilih CPU =====
    cpu_budget = int(budget * allocation['cpu'])
    cpu, over = select_component(cpu_df, cpu_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ CPU melebihi alokasi budget ({cpu_budget:,} → {cpu['price_idr']:,})")
    budget -= cpu['price_idr']

    # ===== Pilih Motherboard dengan Validasi =====
    mb_budget = int(budget * allocation['motherboard'])
    mb_candidates = mb_df[mb_df['socket'] == cpu['socket']]
    
    # Filter motherboard yang kompatibel dengan CPU generation
    compatible_mb = []
    for idx, mb in mb_candidates.iterrows():
        is_valid, msg = validate_cpu_chipset(cpu['model'], mb['chipset'])
        if is_valid:
            compatible_mb.append(idx)
    
    if not compatible_mb:
        errors.append(f"❌ CRITICAL: Tidak ada motherboard yang kompatibel dengan {cpu['model']}")
        mb_candidates_filtered = mb_candidates  # Fallback
    else:
        mb_candidates_filtered = mb_candidates.loc[compatible_mb]
    
    motherboard, over = select_component(mb_candidates_filtered, mb_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ Motherboard melebihi alokasi budget")
    
    # Validasi CPU-Chipset
    is_valid, msg = validate_cpu_chipset(cpu['model'], motherboard['chipset'])
    if not is_valid:
        errors.append(f"❌ {msg}")
    
    # Validasi K-series
    is_valid, msg = validate_k_series_chipset(cpu['model'], motherboard['chipset'])
    if not is_valid:
        warnings.append(f"⚠️ {msg}")
    
    budget -= motherboard['price_idr']

    # ===== Pilih RAM dengan Validasi Type =====
    ram_budget = int(budget * allocation['ram'])
    
    # Filter RAM yang sesuai dengan motherboard
    ram_candidates = ram_df[ram_df['type'] == motherboard['ram_type']]
    
    if len(ram_candidates) == 0:
        errors.append(f"❌ CRITICAL: Tidak ada RAM {motherboard['ram_type']} yang tersedia!")
        ram_candidates = ram_df  # Fallback
    
    ram, over = select_component(ram_candidates, ram_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ RAM melebihi alokasi budget")
    
    # Validasi RAM Type
    is_valid, msg = validate_ram_type(cpu['model'], motherboard['ram_type'], ram['type'])
    if not is_valid:
        errors.append(f"❌ {msg}")
    
    budget -= ram['price_idr']

    # ===== Pilih Storage =====
    storage_budget = int(budget * allocation['storage'])
    storage, over = select_component(storage_df, storage_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ Storage melebihi alokasi budget")
    budget -= storage['price_idr']

    # ===== Pilih Case =====
    case_budget = int(budget * allocation['case'])
    case, over = select_component(case_df, case_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ Case melebihi alokasi budget")
    budget -= case['price_idr']

    # ===== Pilih GPU =====
    gpu_budget = int(budget * allocation['gpu'])
    gpu_candidates = gpu_df[gpu_df['length_mm'] <= case['gpu_max_length_mm']]
    gpu, over = select_component(gpu_candidates, gpu_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ GPU melebihi alokasi budget")
    budget -= gpu['price_idr']

    # ===== Pilih PSU dengan Validasi Wattage =====
    # Hitung required PSU dengan formula yang benar
    cpu_max_tdp = CPU_TDP_MAX.get(cpu['model'], cpu['tdp'])
    required_psu = int((cpu_max_tdp + gpu['tdp']) * 1.5 + 100)
    
    psu_budget = int(budget * allocation['psu'])
    psu_candidates = psu_df[psu_df['power'] >= required_psu]
    
    if len(psu_candidates) == 0:
        errors.append(f"❌ CRITICAL: Tidak ada PSU yang cukup kuat! Minimum {required_psu}W dibutuhkan")
        psu_candidates = psu_df  # Fallback
    
    psu, over = select_component(psu_candidates, psu_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ PSU melebihi alokasi budget")
    
    # Validasi PSU Wattage
    is_valid, msg = validate_psu_wattage(cpu['model'], gpu['tdp'], psu['power'])
    if not is_valid:
        errors.append(f"❌ {msg}")
    
    budget -= psu['power']

    # ===== Pilih Cooling dengan Validasi Capacity =====
    cooling_budget = int(budget * allocation['cooling'])
    
    # Filter cooling yang cukup untuk CPU
    cooling_candidates = cooling_df.copy()
    sufficient_cooling = []
    
    for idx, cool in cooling_candidates.iterrows():
        capacity = COOLING_CAPACITY.get(cool['model'], 100)
        if capacity >= cpu_max_tdp:
            sufficient_cooling.append(idx)
    
    if not sufficient_cooling:
        errors.append(f"❌ CRITICAL: Tidak ada cooling yang cukup untuk CPU {cpu['model']} ({cpu_max_tdp}W)!")
        cooling_candidates_filtered = cooling_candidates  # Fallback
    else:
        cooling_candidates_filtered = cooling_candidates.loc[sufficient_cooling]
    
    cooling, over = select_component(cooling_candidates_filtered, cooling_budget, allow_over=True)
    if over:
        warnings.append(f"⚠️ Cooling melebihi alokasi budget")
    
    # Validasi Cooling Capacity
    is_valid, msg = validate_cooling_capacity(cpu['model'], cooling['model'])
    if not is_valid:
        errors.append(f"❌ {msg}")
    elif msg:  # Ada warning
        warnings.append(msg)

    # ===== Total Harga =====
    total_price = (cpu['price_idr'] + motherboard['price_idr'] + ram['price_idr'] +
                   storage['price_idr'] + case['price_idr'] + gpu['price_idr'] +
                   psu['price_idr'] + cooling['price_idr'])

    # ===== Additional Checks =====
    if gpu['length_mm'] > case['gpu_max_length_mm']:
        errors.append(f"❌ GPU terlalu panjang untuk case ({gpu['length_mm']}mm > {case['gpu_max_length_mm']}mm)")
    
    # Check budget balance
    cpu_gpu_ratio = cpu['price_idr'] / (gpu['price_idr'] + 1)  # +1 to avoid division by zero
    if cpu_gpu_ratio > 2.0:
        warnings.append(f"⚠️ Balance tidak optimal: CPU terlalu mahal dibanding GPU (ratio {cpu_gpu_ratio:.1f}:1)")
    
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
        'errors': errors,
        'warnings': warnings,
        'notes': notes,
        'required_psu_wattage': required_psu,
        'cpu_max_tdp': cpu_max_tdp
    }

    return build, total_price