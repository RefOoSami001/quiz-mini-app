import requests


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

    def generate_questions(self, text: str, number: int, question_type: str):
        json_data = {
            'article': text,
            'totalQuestions': number,
            'questionType': question_type,
            'difficulty': 'hard',
            'additionalInput': 3,
            'language': 'English',
        }
        response = requests.post(
            'https://dashboard.questiongeneratorai.com/api/openAi',
            headers=self.headers,
            json=json_data,
            timeout=60,
        )
        data = response.json()
        return True, data

import requests
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

    def generate_questions(self, text, number, questionType):
        json_data = {
            'article': text,
            'totalQuestions': number,
            'questionType': questionType,
            'difficulty': 'hard',
            'additionalInput': 3,
            'language': 'English',
        }
        response = requests.post('https://dashboard.questiongeneratorai.com/api/openAi', headers=self.headers, json=json_data)
        print(response.json())
        return response.json()
mcq = MCQGeneratorAPI3()
mcq.generate_questions("Respiratory Failure: Causes, Types, Symptoms, and Management",5,"true/false")
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
