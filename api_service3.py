import requests


class MCQGeneratorAPI3:
    def __init__(self):
        self.cookies = {
            'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IjhHVEI3SzBZdGlGYTN2R3VyQ1F1Y3c9PSIsInZhbHVlIjoiZC9sTVp2RjhoRkp2ZU5IYTJGWXE0VVROLzNoVENCSzVnTWhDbDFsdmhBQWl3bEluQTBIUWh0NkpJc24zWTlVQnBVTTRaMWM3M21oYkoxTXArMGJtZDI5aXRnc01Wb3BBYzd5UWdsM2paK3JiWGd5VXQ5bW8xOTRac1AvYnFadmo4OWxZWnBQS012MS9uZncwdmM1Q1NRcUU4Z2ZkVUpVVm9XOURIekRTNHRETDFTbnBtUDZkK2FOUzBqcE5DVk51VVVEQmlFeXBWSGxvdDR4UnVRbU1RbWNaaTUxU092QWhyMVdoQWJBWGJzND0iLCJtYWMiOiIwZjQyYTM3OWYzNTg3ZTA4ZjRlZDc1MzViYmFjMmVhODFhMjQ3MGJmOTYyNzliMWZmZTRhNWMxNTU5MTk0MDBlIiwidGFnIjoiIn0%3D',
            'XSRF-TOKEN': 'eyJpdiI6IlpGUk1TRUZoOG9TWU9wV2xlYkg3OXc9PSIsInZhbHVlIjoiMVBPZUx3d1NLSEJaKzV4SU50K3pMVFM2NXk0alQ1d2lkVi9IYnVRSk1EQ2FUQjhmN2ZLWWdQK2dqeVZ1Um1jelJNS1dFbm04NUc3UVZoZDdWK2dGS2dicmRpdFIzb1FnNSt5akRiRkpDSjRIU1ZZbWVONG5uMllLdURhb3VSYWkiLCJtYWMiOiIyZTRhYmJiMzAxM2I2MjExYTE0M2ViZmM2N2NlY2JhYWQ3NWRjMzcxYTA2NTIxODRhMzEzZjM0M2Y5NGRlMTAwIiwidGFnIjoiIn0%3D',
            'aisurveybuilder_session': 'eyJpdiI6ImhqU2Y3ejM3MDdJeXZwUDJudnRHM0E9PSIsInZhbHVlIjoiZFFxRDNPU1BWR1NYQkY4M3ZzTks1VGFJWFdOcjBCSEVENGFrU3hNS3UyT05iS2JnYTVES3E4T1h3OTdIVUNWSTVuUTExdkxCSXhjYTl2bk5PSDExb01MRENXNTVtVkZTeGtaMFhFWjU2VUE5L3NYZTNjcUxxcUtMbUdaV0tLOHUiLCJtYWMiOiJjMTRiNDIyNjgzM2ZjZjEwZTk2M2YyNDM0ZjEwMDAyNmM0ZmFiN2E2ODEzMTllZWQxM2E5ZDc5N2NlZDdhNzA3IiwidGFnIjoiIn0%3D',
            '_dd_s': 'logs=1&id=8033c6fc-fd55-4c5b-8926-f1fba894f7d1&created=1765367940934&expire=1765369472605',
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
            'x-csrf-token': 'hGhQBnsizc7rxrsIo3SaWaNYgouhgaRs4AtQeCif',
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
