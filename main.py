from recommender import recommend_pc

def format_rupiah(amount):
    return f"Rp{amount:,.0f}".replace(",", ".")

def main():
    print("=" * 50)
    print("    SISTEM REKOMENDASI RAKIT PC - FIXED v2.0")
    print("=" * 50)
    
    try:
        budget = int(input("\nMasukkan budget Anda (dalam Rupiah): "))
        
        if budget < 5_000_000:
            print("⚠️ Budget terlalu rendah untuk rakit PC gaming/productivity yang layak (minimum ~Rp5 juta)")
            return
        
        print("\n🔍 Memproses rekomendasi...")
        build, total_price = recommend_pc(budget)

        # ===== TAMPILKAN HASIL =====
        print("\n" + "=" * 50)
        print("📦 REKOMENDASI RAKITAN PC ANDA:")
        print("=" * 50)
        
        # Komponen
        components = ['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'case', 'cooling']
        
        for key in components:
            item = build[key]
            name = item.get('model', item.get('nama', 'Unknown'))
            price = format_rupiah(item['price_idr'])
            
            # Format line
            line = f"- {key.upper():12} : {name:40} | {price}"
            
            # Info tambahan
            if key == 'gpu':
                line += f"\n  {'':15} TDP: {item['tdp']}W | Panjang: {item['length_mm']}mm"
            elif key == 'ram':
                line += f"\n  {'':15} Tipe: {item['type']} | Speed: {item['speed']}"
            elif key == 'psu':
                line += f"\n  {'':15} Power: {item['power']}W | {item['efficiency']} | {item['modular']}"
            elif key == 'cpu':
                line += f"\n  {'':15} TDP: {item['tdp']}W (Max: {build['cpu_max_tdp']}W) | Socket: {item['socket']}"
            elif key == 'motherboard':
                line += f"\n  {'':15} Chipset: {item['chipset']} | RAM Type: {item['ram_type']}"
            
            print(line)

        # Total & Budget
        print("\n" + "-" * 50)
        print(f"💰 Total Harga      : {format_rupiah(total_price)}")
        print(f"💵 Budget Anda      : {format_rupiah(budget)}")
        print(f"💸 Sisa Budget      : {format_rupiah(budget - total_price)}")
        print(f"📊 Recommended PSU  : {build['required_psu_wattage']}W minimum")
        print("-" * 50)

        # ===== STATUS VALIDASI =====
        print("\n" + "=" * 50)
        print("✅ STATUS VALIDASI:")
        print("=" * 50)
        
        has_errors = len(build['errors']) > 0
        has_warnings = len(build['warnings']) > 0
        
        if not has_errors and not has_warnings:
            print("✅ SEMPURNA! Semua komponen kompatibel dan optimal!")
            print("✅ Build ini siap dirakit tanpa masalah.")
        else:
            if has_errors:
                print("\n❌ CRITICAL ERRORS (Build TIDAK BISA dipakai!):")
                print("-" * 50)
                for i, error in enumerate(build['errors'], 1):
                    print(f"{i}. {error}")
                print("\n⚠️  BUILD INI TIDAK AKAN BERFUNGSI! Jangan beli komponen ini!")
            
            if has_warnings:
                print("\n⚠️  WARNINGS (Build bisa dipakai, tapi tidak optimal):")
                print("-" * 50)
                for i, warning in enumerate(build['warnings'], 1):
                    print(f"{i}. {warning}")
                print("\n💡 Pertimbangkan untuk mengoptimalkan komponen di atas.")
        
        # Budget status
        print("\n" + "=" * 50)
        if total_price <= budget:
            over_budget = False
            print("✅ BUDGET: Rekomendasi sesuai dengan budget Anda.")
            if budget - total_price > 1_000_000:
                print(f"💡 Tip: Anda masih punya sisa {format_rupiah(budget - total_price)}")
                print("   Pertimbangkan upgrade GPU, RAM, atau storage!")
        else:
            over_budget = True
            print(f"❌ BUDGET: Rekomendasi melebihi budget sebesar {format_rupiah(total_price - budget)}")
        
        print("=" * 50)
        
        # ===== FINAL VERDICT =====
        print("\n" + "=" * 50)
        print("📋 KESIMPULAN AKHIR:")
        print("=" * 50)
        
        if has_errors:
            print("❌ BUILD TIDAK VALID - JANGAN BELI!")
            print("   Komponen tidak kompatibel satu sama lain.")
            print("   Sistem tidak akan berfungsi dengan build ini.")
        elif over_budget:
            print("⚠️  BUILD VALID tapi MELEBIHI BUDGET")
            print("   Pertimbangkan untuk meningkatkan budget atau")
            print("   downgrade beberapa komponen.")
        elif has_warnings:
            print("⚠️  BUILD VALID dengan PERINGATAN")
            print("   Build ini akan berfungsi, tapi tidak optimal.")
            print("   Pertimbangkan saran di atas untuk hasil terbaik.")
        else:
            print("✅ BUILD SEMPURNA!")
            print("   Semua komponen kompatibel dan optimal.")
            print("   Silakan lanjutkan pembelian! 🎉")
        
        print("=" * 50)

    except ValueError as e:
        print(f"\n❌ Error: Input tidak valid - {e}")
    except KeyError as e:
        print(f"\n❌ Error: Data tidak lengkap - {e}")
    except Exception as e:
        print(f"\n❌ Error tidak terduga: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()