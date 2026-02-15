# find_duplicate_certificate.py
import re


def find_certificate_duplicates(filename='run.py'):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    print("=" * 60)
    print(f"Searching for duplicate 'generate_certificate' in {filename}")
    print("=" * 60)

    # Find all function definitions
    function_lines = []
    route_lines = []

    for i, line in enumerate(lines, 1):
        if 'def generate_certificate' in line:
            function_lines.append(i)
            print(f"\n🔍 Found function definition at line {i}:")
            print(f"   {line.strip()}")

            # Show context (the route decorator above it)
            if i > 1 and '@app.route' in lines[i - 2]:
                print(f"   Route decorator at line {i - 2}: {lines[i - 2].strip()}")
            if i > 0 and '@login_required' in lines[i - 1]:
                print(f"   Login decorator at line {i - 1}: {lines[i - 1].strip()}")

        if '@app.route' in line and 'certificate' in line:
            route_lines.append(i)
            print(f"\n📍 Found certificate route at line {i}:")
            print(f"   {line.strip()}")

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    print(f"Total 'generate_certificate' functions found: {len(function_lines)}")
    print(f"Total certificate routes found: {len(route_lines)}")

    if len(function_lines) > 1:
        print("\n❌ ERROR: Multiple generate_certificate functions found at lines:", function_lines)
        print("\nTo fix this, you need to delete all but one of these functions.")
        print("Keep the one with the complete implementation and delete the others.")
    elif len(function_lines) == 1:
        print("\n✅ CORRECT: Only one generate_certificate function found.")
    else:
        print("\n⚠️  WARNING: No generate_certificate function found!")

    if len(route_lines) > 1:
        print(f"\n❌ ERROR: Multiple certificate routes found at lines:", route_lines)

    return function_lines, route_lines


if __name__ == '__main__':
    find_certificate_duplicates()