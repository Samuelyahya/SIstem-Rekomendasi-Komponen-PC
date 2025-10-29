from recommender import recommend_pc

def format_rupiah(amount):
    return f"Rp{amount:,.0f}".replace(",", ".")

def check_compatibility(build):
    notes = []

    if build['gpu']['length_mm'] > build['case']['gpu_max_length_mm']:
        notes.append(f"GPU terlalu panjang untuk case ({build['gpu']['length_mm']}mm > {build['case']['gpu_max_length_mm']}mm)")

    total_tdp = build['cpu']['tdp'] + build['gpu']['tdp']
    if build['psu']['power'] < total_tdp:
        notes.append(f"PSU tidak cukup kuat (dibutuhkan {total_tdp}W, PSU hanya {build['psu']['power']}W)")

    return notes

def main():
    print("=== Sistem Rekomendasi Rakit PC ===")
    try:
        budget = int(input("Masukkan budget Anda (dalam Rupiah): "))
        build, total_price = recommend_pc(budget)

        # Cek kompatibilitas
        build['notes'] = check_compatibility(build)

        # Tampilin hasil
        print("\nRekomendasi rakitan PC Anda:")
        for key in ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling']:
            item = build[key]
            line = f"- {key.upper()}: {item.get('model', item.get('nama', 'Unknown'))} | Rp{item['price_idr']:,}"
            # Tambahan info untuk GPU
            if key == 'gpu':
                line += f" | TDP: {item['tdp']}W | Panjang GPU: {item['length_mm']} mm"
            # Tambahan info untuk RAM
            if key == 'ram':
                line += f" | Tipe: {item.get('type','')}"
            # Tambahan info untuk PSU
            if key == 'psu':
                line += f" | Power: {item['power']}W"
            print(line)

        print(f"\nTotal estimasi harga: {format_rupiah(total_price)}")

        if build['notes']:
            print("⚠️ Komponen tidak sepenuhnya kompatibel:")
            for note in build['notes']:
                print(f"- {note}")
        else:
            print("✅ Semua komponen kompatibel.")

        if total_price <= budget:
            print("✅ Rekomendasi sesuai dengan budget Anda.")
        else:
            print("⚠️ Rekomendasi melebihi budget!")

    except ValueError as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
