import requests
from typing import Tuple, Dict, Any


class MCQGeneratorAPI3:
    def __init__(self):
        self.headers = {
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://dashboard.questiongeneratorai.com',
            'priority': 'u=1, i',
            'referer': 'https://dashboard.questiongeneratorai.com/',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        }

    def generate_questions(self, text: str, number: int, question_type: str) -> Tuple[bool, Dict[str, Any]]:
        json_data = {
            'article': text,
            'totalQuestions': number,
            'questionType': question_type,  # 'true/false' or 'Multiple Choice'
            'difficulty': 'hard',
            'additionalInput': 3,
            'language': 'English',
        }
        try:
            response = requests.post(
                'https://dashboard.questiongeneratorai.com/api/openAi',
                headers=self.headers,
                json=json_data,
                timeout=60,
            )
            data = response.json()
        except Exception as e:
            return False, {'error': str(e)}

        # Normalize into model-2-like map: { Q1: { text, options: {A:..}, answer: 'A' }, ... }
        try:
            questions = data.get('questions', [])
            normalized: Dict[str, Any] = {}
            for idx, q in enumerate(questions, start=1):
                key = f"Q{idx}"
                if question_type.lower() in ['true/false', 'true_false', 'tf']:
                    # Expected: { 'question': str, 'correct_answer': 'true'|'false' }
                    text_q = q.get('question', '').strip()
                    correct = str(q.get('correct_answer', '')).strip().lower()
                    options = {'A': 'True', 'B': 'False'}
                    answer = 'A' if correct in ['true', 't', '1'] else 'B'
                    normalized[key] = {
                        'text': text_q,
                        'options': options,
                        'answer': answer,
                    }
                else:
                    # Multiple Choice expected: options like "A) text" and correct_answer like "A) text"
                    text_q = q.get('question', '').strip()
                    raw_options = q.get('options', []) or []
                    options = {}
                    for opt in raw_options:
                        s = str(opt)
                        # Detect pattern "X) value"; fallback to sequential letters
                        if ")" in s and len(s) >= 3:
                            letter = s.split(")", 1)[0].strip().replace('(', '').replace(')', '')
                            value = s.split(")", 1)[1].strip()
                        else:
                            letter = chr(ord('A') + len(options))
                            value = s
                        letter = letter[0].upper()
                        options[letter] = value
                    correct_s = str(q.get('correct_answer', '')).strip()
                    # Extract the correct letter
                    if ")" in correct_s:
                        correct_letter = correct_s.split(")", 1)[0].strip().replace('(', '').replace(')', '')
                    else:
                        correct_letter = correct_s[:1]
                    correct_letter = (correct_letter or 'A')[0].upper()
                    normalized[key] = {
                        'text': text_q,
                        'options': options,
                        'answer': correct_letter if correct_letter in options else 'A',
                    }
            return True, normalized
        except Exception as e:
            return False, {'error': f'Normalization error: {str(e)}'}
#response example:
#true/false:
#{'title': 'Generated Questions', 'questions': [{'question': 'Respiratory failure is considered a disease by itself.', 'correct_answer': 'false'}, {'question': 'Prompt recognition and treatment are not critical in cases of respiratory failure.', 'correct_answer': 'false'}, {'question': 'Hypercapnic respiratory failure is characterized by low levels of oxygen in the blood.', 'correct_answer': 'false'}, {'question': 'Pulse oximetry is an invasive method for monitoring oxygen saturation.', 'correct_answer': 'false'}, {'question': 'Bronchodilators and corticosteroids are used for treating infections in respiratory failure.', 'correct_answer': 'false'}, {'question': 'Chronic respiratory failure often requires ongoing support and may not be reversible.', 'correct_answer': 'true'}]}

#Multiple Choice:
# {
#     "title": "Generated Questions",
#     "questions": [
#         {
#             "question": "When was the Macintosh computer introduced by Steve Jobs?",
#             "options": [
#                 "A) 1984",
#                 "B) 1990",
#                 "C) 2001",
#                 "D) 2007"
#             ],
#             "correct_answer": "A) 1984"
#         },
#         {
#             "question": "Which product redefined the way people consume music and became a cultural phenomenon?",
#             "options": [
#                 "A) iPod",
#                 "B) iPhone",
#                 "C) iPad",
#                 "D) Macintosh"
#             ],
#             "correct_answer": "A) iPod"
#         },
#         {
#             "question": "In which year was the iPhone launched by Steve Jobs, marking a paradigm shift in mobile communication?",
#             "options": [
#                 "A) 2001",
#                 "B) 2004",
#                 "C) 2007",
#                 "D) 2010"
#             ],
#             "correct_answer": "C) 2007"
#         },
#         {
#             "question": "Which industry did the iPhone influence beyond technology?",
#             "options": [
#                 "A) Music",
#                 "B) Photography",
#                 "C) Food",
#                 "D) Fashion"
#             ],
#             "correct_answer": "B) Photography"
#         }
#     ]
# }
