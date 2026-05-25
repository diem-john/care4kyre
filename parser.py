# import os
# import re
# import json
# from pathlib import Path
#
# RAW_DATA_DIR = Path("data/raw")
#
#
# def parse_markdown_content(content):
#     """
#     Parses the raw text using the highly robust line-by-line extraction method.
#     """
#     questions_data = []
#
#     # 1. Split into Questions Section and Answers Section
#     split_match = re.search(r'Answers?\s+and\s+Rationales?|Answers?\s*:\s*\n|Answer Key\s*\n', content, re.IGNORECASE)
#
#     if split_match:
#         q_section = content[:split_match.start()]
#         a_section = content[split_match.end():]
#     else:
#         # Fallback split
#         halfway = len(content) // 2
#         fallback_match = re.search(r'\n(?:Answer:\s*)?(?:1\.?\s*)?[\(]?[A-D][\)]?[\.\s]', content[halfway:],
#                                    re.IGNORECASE)
#         if fallback_match:
#             q_section = content[:halfway + fallback_match.start()]
#             a_section = content[halfway + fallback_match.start():]
#         else:
#             return []
#
#             # 2. Extract Questions (Line-by-line scanning)
#     question_starts = list(re.finditer(r'^(\d+)\.[\s]*', q_section, re.MULTILINE))
#
#     raw_questions = []
#     for idx, match in enumerate(question_starts):
#         start_pos = match.end()
#         end_pos = question_starts[idx + 1].start() if idx + 1 < len(question_starts) else len(q_section)
#         q_text = q_section[start_pos:end_pos].strip()
#         raw_questions.append(q_text)
#
#     # 3. Extract Answers and Rationales (Line-by-line scanning)
#     answer_pattern = r'^(?:Answer\s*:?\s*(?:\d+\.?\s*)?[\(]?([A-D])[\)]?|(?:\d+\.?\s*)?[\(]([A-D])[\)]|(?:\d+\.?\s*)?([A-D])[\.\)])[\s:-]+'
#     answer_starts = list(re.finditer(answer_pattern, a_section, re.MULTILINE | re.IGNORECASE))
#
#     raw_answers = []
#     for idx, match in enumerate(answer_starts):
#         ans_letter = match.group(1) or match.group(2) or match.group(3)
#         ans_letter = ans_letter.upper()
#
#         start_pos = match.end()
#         end_pos = answer_starts[idx + 1].start() if idx + 1 < len(answer_starts) else len(a_section)
#         rationale = a_section[start_pos:end_pos].strip()
#         raw_answers.append((ans_letter, rationale))
#
#     # 4. Map them together safely
#     max_index = min(len(raw_questions), len(raw_answers))
#
#     for i in range(max_index):
#         q_text = raw_questions[i]
#         ans_letter, ans_rationale = raw_answers[i]
#
#         # Process choices
#         lines = [line.strip() for line in q_text.split('\n') if line.strip()]
#
#         if len(lines) >= 5:
#             question_main = " ".join(lines[:-4])
#             choice_lines = lines[-4:]
#         else:
#             question_main = " ".join(lines)
#             choice_lines = []
#
#         # Clean choices
#         choices_dict = {}
#         for j, letter in enumerate(["A", "B", "C", "D"]):
#             if j < len(choice_lines):
#                 clean_choice = re.sub(r'^[\(]?[A-D][\)\.]?\s*', '', choice_lines[j], flags=re.IGNORECASE)
#                 choices_dict[letter] = clean_choice
#             else:
#                 choices_dict[letter] = "Option unavailable"
#
#         questions_data.append({
#             "question": question_main,
#             "choices": choices_dict,
#             "correct_answer": ans_letter,
#             "rationale": ans_rationale.replace('\n', ' ')
#         })
#
#     return questions_data
#
#
# def build_modular_database():
#     if not RAW_DATA_DIR.exists():
#         print(f"Error: Could not find directory {RAW_DATA_DIR}")
#         return
#
#     total_files = 0
#     total_questions = 0
#
#     for category_dir in RAW_DATA_DIR.iterdir():
#         if category_dir.is_dir():
#             print(f"\nProcessing Folder: {category_dir.name}")
#
#             # Create the json_files subfolder inside the current category
#             json_dir = category_dir / "json_files"
#             json_dir.mkdir(exist_ok=True)
#
#             for md_file in category_dir.glob("*.md"):
#                 with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
#                     content = f.read()
#
#                 parsed_questions = parse_markdown_content(content)
#
#                 if parsed_questions:
#                     # Save individually! Example: data/raw/chn/json_files/pnle1.json
#                     json_file_path = json_dir / f"{md_file.stem}.json"
#
#                     with open(json_file_path, 'w', encoding='utf-8') as f:
#                         json.dump(parsed_questions, f, indent=2)
#
#                     print(f"  ✅ Saved {json_file_path.name} ({len(parsed_questions)} questions)")
#                     total_files += 1
#                     total_questions += len(parsed_questions)
#                 else:
#                     print(f"  ❌ WARNING: Could not parse {md_file.name}")
#
#     print(f"\n🎉 Done! Generated {total_files} JSON files containing {total_questions} total questions.")
#
#
# if __name__ == "__main__":
#     build_modular_database()