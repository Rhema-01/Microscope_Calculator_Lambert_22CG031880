"""
Phase A: Core Calculation Program
Microscope Specimen Size Calculator
CSC 442 - Project 1
"""

# Microscope types and their magnification factors
MICROSCOPE_TYPES = {
    "1": ("Light Microscope (Low Power)",       40),
    "2": ("Light Microscope (Medium Power)",    100),
    "3": ("Light Microscope (High Power)",      400),
    "4": ("Light Microscope (Oil Immersion)",  1000),
    "5": ("Stereo / Dissecting Microscope",      20),
    "6": ("Scanning Electron Microscope (SEM)", 10000),
    "7": ("Transmission Electron Microscope (TEM)", 50000),
    "8": ("Confocal Microscope",                600),
}

# Output unit conversion factors (from mm)
UNIT_CONVERSIONS = {
    "1": ("nm",  1_000_000),
    "2": ("µm",  1_000),
    "3": ("mm",  1),
    "4": ("cm",  0.1),
    "5": ("m",   0.001),
}


def display_microscope_menu():
    print("\n--- Select Microscope Type ---")
    for key, (name, mag) in MICROSCOPE_TYPES.items():
        print(f"  [{key}] {name}  (×{mag:,})")


def display_unit_menu():
    print("\n--- Select Output Unit ---")
    for key, (unit, _) in UNIT_CONVERSIONS.items():
        print(f"  [{key}] {unit}")


def get_microscope_choice():
    while True:
        display_microscope_menu()
        choice = input("\nEnter choice [1-8]: ").strip()
        if choice in MICROSCOPE_TYPES:
            return choice
        print("  Invalid choice. Please select a number from the list.")


def get_unit_choice():
    while True:
        display_unit_menu()
        choice = input("\nEnter choice [1-5]: ").strip()
        if choice in UNIT_CONVERSIONS:
            return choice
        print("  Invalid choice. Please select a number from the list.")


def get_measured_size():
    while True:
        try:
            size = float(input("\nEnter the specimen size as measured from microscope image (in mm): ").strip())
            if size <= 0:
                print("  Size must be a positive number.")
                continue
            return size
        except ValueError:
            print("  Invalid input. Please enter a numeric value.")


def calculate_real_size(measured_mm, magnification, unit_factor):
    real_mm = measured_mm / magnification
    return real_mm * unit_factor


def display_result(measured_mm, microscope_name, magnification, unit_name, real_size):
    print("\n" + "=" * 55)
    print("          CALCULATION RESULT")
    print("=" * 55)
    print(f"  Microscope Type  : {microscope_name}")
    print(f"  Magnification    : ×{magnification:,}")
    print(f"  Measured Size    : {measured_mm} mm")
    print(f"  Formula Used     : Real Size = Measured Size ÷ Magnification")
    print(f"  Calculation      : {measured_mm} ÷ {magnification:,} = {measured_mm/magnification:.6f} mm")
    print(f"  Real Size        : {real_size:.6f} {unit_name}")
    print("=" * 55)
    return real_size


def run():
    print("\n" + "=" * 55)
    print("   MICROSCOPE SPECIMEN SIZE CALCULATOR — Phase A")
    print("=" * 55)

    while True:
        measured_mm  = get_measured_size()
        mic_choice   = get_microscope_choice()
        unit_choice  = get_unit_choice()

        microscope_name, magnification = MICROSCOPE_TYPES[mic_choice]
        unit_name, unit_factor         = UNIT_CONVERSIONS[unit_choice]

        real_size = calculate_real_size(measured_mm, magnification, unit_factor)
        display_result(measured_mm, microscope_name, magnification, unit_name, real_size)

        again = input("\nPerform another calculation? (y/n): ").strip().lower()
        if again != 'y':
            print("\nGoodbye!\n")
            break


if __name__ == "__main__":
    run()
