import requests


class MCQGeneratorAPI3:
    def __init__(self):
        self.cookies = {
            'XSRF-TOKEN': 'eyJpdiI6IlE3TkJCWDMxU1Zka1dsYlVFWll3b3c9PSIsInZhbHVlIjoicTUyeXMyT0ptVjZxTTRwc0tsS3RMTExaVEFac1dEY21HNHRJdVoxU1FQTjZIYmY4d2w3VVpiUTI0WFc2Q05MRHlmajJHbGtaZGZMNlRxYUUwL243d05waVhDYXlSYUMwOEt4SGNGaDVDZUh3Q1ZiSEZ4eEtiUTBjalc4cllSM3UiLCJtYWMiOiI5NzUxMTMwODhkM2U2MjlhMjhiMjBjZGNkNzMzOTcyNTAyY2U5NjA4ODQ4ZGNkNDc1NGI5NDAzMDU5MWU2ZGM5IiwidGFnIjoiIn0%3D',
            'aisurveybuilder_session': 'eyJpdiI6IjF5bDJ4TDRYekxOdlZYaElmNEt3dVE9PSIsInZhbHVlIjoiS2laaUdNNTdydlVxNjFJTTlFMFdkZ016dEpOZi9KbkI1NW5wYXhOZ1FOay9GM3VwZUFha2c2dkx6MFVzcEYzTXZrUDF0NFEyUjVBTWd3UkhuME81dDErMEw2c25tL0JJYnR3Nkl3SFhNSnRadkJ2MFY1SDJaU3lkSGV2Q2tRZnoiLCJtYWMiOiIwZWQwMDBlZDhmZDY4ZGY1Y2VhZjYwZGMxNTNiMTY1MjNlODFiNTEzZWJjYWRjOGY1YjE4NWE3ODk5NzhiMjk2IiwidGFnIjoiIn0%3D',
            '_dd_s': 'logs=1&id=856597cf-cb2b-458e-aa1f-cdb35fc220c8&created=1765317216841&expire=1765318468773',
        }
        
        self.headers = {
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://app.aisurveymaker.com',
            'priority': 'u=1, i',
            'referer': 'https://app.aisurveymaker.com/quiz/create',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'x-csrf-token': 'eyz7EYy9S29STvEIastlqz56V7fv2jRyiadBzXln',
            'x-requested-with': 'XMLHttpRequest',
        }

    def generate_questions(self, text: str, number: int, question_type: str):
        # Map question_type to API format
        # 'true/false' or 'True/False' -> 'true_false'
        # 'Multiple Choice' or 'mcq' -> 'mcq'
        # 'short answer' or 'Short Answer' -> 'short_answer'
        if question_type.lower() in ['true/false', 'true-false', 'true false']:
            api_question_type = 'true_false'
        elif question_type.lower() in ['multiple choice', 'mcq', 'multiple-choice']:
            api_question_type = 'mcq'
        elif question_type.lower() in ['short answer', 'short-answer', 'shortanswer']:
            api_question_type = 'short_answer'
        else:
            api_question_type = question_type.lower().replace(' ', '_').replace('/', '_')
        
        files = {
            'question_type': (None, api_question_type),
            'question_count': (None, str(number)),
            'difficulty': (None, 'hard'),
            'language': (None, 'English'),
            'input_text': (None, str(text)),
        }
        
        response = requests.post(
            'https://app.aisurveymaker.com/quiz/generate',
            cookies=self.cookies,
            headers=self.headers,
            files=files,
            timeout=60,
        )
        data = response.json()
        return True, data
