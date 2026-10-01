# eval/judge.py
def judge_answer(answer, expected_keywords):
    answer_lower = answer.lower()
    return any(kw.lower() in answer_lower for kw in expected_keywords)