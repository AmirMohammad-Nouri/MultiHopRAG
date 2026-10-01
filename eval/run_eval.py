# eval/run_eval.py
import json
from eval.modes import MODES
from eval.judge import judge_answer
from synthesis.answer import synthesize

def run_eval(questions_path="eval/eval_questions.json"):
    with open(questions_path) as f:
        questions = json.load(f)

    results = {mode: {"single_hop": [], "multi_hop": []} for mode in MODES}
    detailed_log = []

    for q in questions:
        for mode_name, retrieve_fn in MODES.items():
            retrieval = retrieve_fn(q["question"])
            answer = synthesize(q["question"], retrieval)
            correct = judge_answer(answer, q["expected_keywords"])

            results[mode_name][q["type"]].append(correct)
            detailed_log.append({
                "question_id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "mode": mode_name,
                "answer": answer,
                "correct": correct,
            })
            print(f"[{mode_name}] {q['id']} ({q['type']}): {'PASS' if correct else 'FAIL'}")

    with open("eval/results_detailed.json", "w") as f:
        json.dump(detailed_log, f, indent=2)

    print("\n=== SUMMARY ===")
    print(f"{'Mode':<15}{'Single-hop':<15}{'Multi-hop':<15}")
    summary = {}
    for mode_name, by_type in results.items():
        single = by_type["single_hop"]
        multi = by_type["multi_hop"]
        single_acc = sum(single) / len(single) if single else None
        multi_acc = sum(multi) / len(multi) if multi else None
        summary[mode_name] = {"single_hop": single_acc, "multi_hop": multi_acc}
        s_str = f"{single_acc:.0%}" if single_acc is not None else "N/A"
        m_str = f"{multi_acc:.0%}" if multi_acc is not None else "N/A"
        print(f"{mode_name:<15}{s_str:<15}{m_str:<15}")

    with open("eval/results_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary

if __name__ == "__main__":
    run_eval()