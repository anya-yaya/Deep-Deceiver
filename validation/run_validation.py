import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from dataset import VALIDATION_DATASET
from metrics import calculate_metrics

from app.detection.fast_filter import fast_filter
from app.agents.sentry import Sentry
from app.agents.analyst import Analyst
from app.agents.orchestrator import Orchestrator


def run_validation():

    dataset = VALIDATION_DATASET

    sentry = Sentry()
    analyst = Analyst()
    orchestrator = Orchestrator()

    results = []

    print("=" * 70)
    print("DEEP-DECEIVER SECURITY VALIDATION")
    print("=" * 70)

    for case in dataset:

        text = case["text"]

        # --------------------------------------------------------
        # 1. FAST FILTER
        # --------------------------------------------------------

        filter_result = fast_filter(text)

        # --------------------------------------------------------
        # 2. SENTRY
        # --------------------------------------------------------

        sentry_result = sentry.analyze(text)

        # --------------------------------------------------------
        # 3. ANALYST
        # --------------------------------------------------------

        analyst_result = analyst.analyze(
            text,
            filter_result,
            sentry_result
        )

        # --------------------------------------------------------
        # 4. ORCHESTRATOR
        # --------------------------------------------------------

        orchestration_result = orchestrator.decide(
            sentry_result,
            analyst_result
        )

        # --------------------------------------------------------
        # 5. ACTUAL DETECTION
        # --------------------------------------------------------

        detected = (
            orchestration_result["route"] == "shadow"
        )

        expected_attack = case["expected_attack"]

        result = {
            "id": case["id"],
            "category": case["category"],
            "expected": expected_attack,
            "detected": detected,
            "final_risk_score": (
                orchestration_result["final_risk_score"]
            ),
            "route": orchestration_result["route"],
            "action": orchestration_result["action"],
        }

        results.append(result)

        status = (
            "PASS"
            if detected == expected_attack
            else "FAIL"
        )

        print(
            f"{status:<6} "
            f"{case['id']:<18} "
            f"expected={str(expected_attack):<7} "
            f"detected={str(detected):<5} "
            f"risk={result['final_risk_score']:.4f}"
        )

    # ------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------

    metrics = calculate_metrics(results)

    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    print(f"Total Samples        : {metrics['total_samples']}")
    print(f"True Positives       : {metrics['true_positive']}")
    print(f"True Negatives       : {metrics['true_negative']}")
    print(f"False Positives      : {metrics['false_positive']}")
    print(f"False Negatives      : {metrics['false_negative']}")

    print()
    print(
        f"Accuracy             : "
        f"{metrics['accuracy'] * 100:.2f}%"
    )

    print(
        f"Precision            : "
        f"{metrics['precision'] * 100:.2f}%"
    )

    print(
        f"Recall               : "
        f"{metrics['recall'] * 100:.2f}%"
    )

    print(
        f"F1 Score             : "
        f"{metrics['f1_score'] * 100:.2f}%"
    )

    print(
        f"Detection Rate       : "
        f"{metrics['detection_rate'] * 100:.2f}%"
    )

    print(
        f"False Positive Rate  : "
        f"{metrics['false_positive_rate'] * 100:.2f}%"
    )

    print("=" * 70)

    return results, metrics


if __name__ == "__main__":
    run_validation()