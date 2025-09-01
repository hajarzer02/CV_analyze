import os
import json
from cv_extractor_cli import CVExtractor

def main():
    cv_folder = "cv_files"

    output_folder = "outputs"
    extracted_data_folder = "extracted_data"
    os.makedirs(cv_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(extracted_data_folder, exist_ok=True)

    extractor = CVExtractor()
    cv_files = [f for f in os.listdir(cv_folder) if f.lower().endswith((".pdf", ".docx", ".txt"))]

    if not cv_files:
        print(f"No CV files found in {cv_folder}/")
        print("Add PDF, DOCX, or TXT files to analyze")
        return

    print(f"Found {len(cv_files)} CV file(s)\n")


    for i, filename in enumerate(cv_files, 1):
        filepath = os.path.join(cv_folder, filename)
        print(f"[{i}/{len(cv_files)}] {filename}")
        try:
            # Extract raw text and save to extracted_data
            from cv_extractor_cli import load_text
            raw_text = load_text(filepath)
            txt_output_file = os.path.join(extracted_data_folder, f"{os.path.splitext(filename)[0]}.txt")
            with open(txt_output_file, 'w', encoding='utf-8') as txtf:
                txtf.write(raw_text)

            # Now extract structured data and save as JSON
            result = extractor.extract_cv_data(filepath)
            output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved: {output_file}\n")
        except Exception as e:
            print(f"✗ Error: {e}\n")

    print("Extraction complete!")

if __name__ == "__main__":
    main()