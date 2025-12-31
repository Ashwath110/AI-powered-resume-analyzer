# backend/test_parser.py

from resume_parser import ResumeParser

# Use the downloaded dataset
parser = ResumeParser(
    csv_path="datasets/resumes/UpdatedResumeDataSet.csv"
)

parsed_data = parser.save_json("datasets/resumes/parsed_resumes.json")

print("\n" + "="*60)
print("Sample parsed resume:")
print("="*60)
if parsed_data:
    import json
    print(json.dumps(parsed_data[0], indent=2))
