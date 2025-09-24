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
            'additionalInput': 4,
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
