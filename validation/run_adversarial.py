import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))


from adversarial_tests import ENCODED_TESTS

from app.detection.fast_filter import fast_filter
from app.agents.sentry import Sentry
from app.agents.analyst import Analyst
from app.agents.orchestrator import Orchestrator


def run_adversarial_tests():

    sentry = Sentry()
    analyst = Analyst()
    orchestrator = Orchestrator()

    print("=" * 70)
    print("DEEP-DECEIVER ADVERSARIAL VALIDATION")
    print("=" * 70)

    results = []

    for case in ENCODED_TESTS:

        text = case["text"]

        filter_result = fast_filter(text)

        sentry_result = sentry.analyze(text)

        analyst_result = analyst.analyze(
            text,
            filter_result,
            sentry_result
        )

        orchestration_result = orchestrator.decide(
            sentry_result,
            analyst_result
        )

        detected = (
            orchestration_result["route"] == "shadow"
        )

        passed = (
            detected == (case["expected"] == "attack")
        )

        result = {
            "id": case["id"],
            "category": case["category"],
            "expected": case["expected"],
            "detected": detected,
            "passed": passed,
            "fast_filter_score": filter_result["score"],
            "sentry_score": sentry_result["score"],
            "analyst_score": analyst_result["risk_score"],
            "final_risk_score": (
                orchestration_result["final_risk_score"]
            ),
            "route": orchestration_result["route"],
        }

        results.append(result)

        status = "PASS" if passed else "FAIL"

        print(
            f"{status:<6} "
            f"{case['id']:<15} "
            f"category={case['category']:<20} "
            f"detected={str(detected):<5} "
            f"risk={result['final_risk_score']:.4f}"
        )

        print(
            f"       "
            f"FastFilter={result['fast_filter_score']:.4f} "
            f"Sentry={result['sentry_score']:.4f} "
            f"Analyst={result['analyst_score']:.4f}"
        )

    print()
    print("=" * 70)
    print("ADVERSARIAL SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    print(f"Total Tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    if total:
        print(
            f"Pass Rate   : "
            f"{(passed / total) * 100:.2f}%"
        )

    print("=" * 70)

    return results


if __name__ == "__main__":
    run_adversarial_tests()