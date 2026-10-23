from name_generator import generate_name

for category in ["Personal", "Small Business", "Large Corporation", "Government", "Military"]:
    for _ in range(5):
        print(generate_name(category))