import os

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()


INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")


class InfluxDBService:
    """
    Handles writing and querying forensic events
    stored in InfluxDB.
    """

    def __init__(self):
        if not all([
            INFLUXDB_URL,
            INFLUXDB_TOKEN,
            INFLUXDB_ORG,
            INFLUXDB_BUCKET
        ]):
            raise RuntimeError(
                "InfluxDB configuration is incomplete."
            )

        self.client = InfluxDBClient(
            url=INFLUXDB_URL,
            token=INFLUXDB_TOKEN,
            org=INFLUXDB_ORG
        )

        self.write_api = self.client.write_api(
            write_options=SYNCHRONOUS
        )

        self.query_api = self.client.query_api()

    # --------------------------------------------------
    # WRITE
    # --------------------------------------------------

    def write_event(self, event: dict):
        """
        Store a forensic event in InfluxDB.
        """

        detection = event["detection"]
        analysis = event["analysis"]
        orchestration = event["orchestration"]

        kill_chain = event.get(
            "kill_chain",
            {}
        )

        mitre = event.get(
            "mitre",
            {}
        )

        current_stage = kill_chain.get(
            "current_stage"
        )

        mitre_id = mitre.get(
            "id"
        )

        mitre_tactic = mitre.get(
            "tactic"
        )

        mitre_technique = mitre.get(
            "technique"
        )

        point = (
            Point("forensic_events")

            # ------------------------------
            # Tags
            # ------------------------------

            .tag(
                "session_id",
                event["session_id"]
            )

            .tag(
                "response_source",
                event["response_source"]
            )

            .tag(
                "attack_category",
                analysis["attack_category"]
            )

            .tag(
                "intent",
                analysis["intent"]
            )

            # Kill Chain tag
            .tag(
                "kill_chain_stage",
                current_stage or "unknown"
            )

            # MITRE tags
            .tag(
                "mitre_id",
                mitre_id or "unknown"
            )

            .tag(
                "mitre_technique",
                mitre_technique or "unknown"
            )

            # ------------------------------
            # Fields
            # ------------------------------

            .field(
                "message",
                event["input"]["message"]
            )

            .field(
                "fast_filter_score",
                detection["fast_filter_score"]
            )

            .field(
                "sentry_score",
                detection["sentry_score"]
            )

            .field(
                "sentry_flagged",
                detection["sentry_flagged"]
            )

            .field(
                "risk_score",
                analysis["risk_score"]
            )

            .field(
                "final_risk_score",
                orchestration["final_risk_score"]
            )

            .field(
                "route",
                orchestration["route"]
            )

            .field(
                "action",
                orchestration["action"]
            )

            # Kill Chain progression
            .field(
                "kill_chain_progression",
                kill_chain.get(
                    "attack_progression",
                    0.0
                )
            )

            .field(
                "kill_chain_interaction_count",
                kill_chain.get(
                    "interaction_count",
                    0
                )
            )

            # MITRE tactic
            .field(
                "mitre_tactic",
                mitre_tactic or "unknown"
            )
        )

        self.write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    def query_events(
        self,
        time_range: str = "-24h",
        limit: int = 100
    ) -> list[dict]:
        """
        Retrieve forensic events from InfluxDB.

        Parameters:
            time_range:
                Flux time range such as "-1h", "-24h", "-7d".

            limit:
                Maximum number of events to return.
        """

        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: {time_range})
            |> filter(fn: (r) =>
                r._measurement == "forensic_events"
            )
            |> pivot(
                rowKey: ["_time"],
                columnKey: ["_field"],
                valueColumn: "_value"
            )
            |> sort(
                columns: ["_time"],
                desc: true
            )
            |> limit(n: {limit})
        '''

        tables = self.query_api.query(
            query=query,
            org=INFLUXDB_ORG
        )

        events = []

        for table in tables:
            for record in table.records:

                values = record.values

                event = {
                    "timestamp": (
                        record.get_time().isoformat()
                        if record.get_time()
                        else None
                    ),

                    "session_id": values.get(
                        "session_id"
                    ),

                    "response_source": values.get(
                        "response_source"
                    ),

                    "attack_category": values.get(
                        "attack_category"
                    ),

                    "intent": values.get(
                        "intent"
                    ),

                    "message": values.get(
                        "message"
                    ),

                    "fast_filter_score": values.get(
                        "fast_filter_score"
                    ),

                    "sentry_score": values.get(
                        "sentry_score"
                    ),

                    "sentry_flagged": values.get(
                        "sentry_flagged"
                    ),

                    "risk_score": values.get(
                        "risk_score"
                    ),

                    "final_risk_score": values.get(
                        "final_risk_score"
                    ),

                    "route": values.get(
                        "route"
                    ),

                    "action": values.get(
                        "action"
                    ),

                    # Kill Chain
                    "kill_chain_stage": values.get(
                        "kill_chain_stage"
                    ),

                    "kill_chain_progression": values.get(
                        "kill_chain_progression"
                    ),

                    "kill_chain_interaction_count": values.get(
                        "kill_chain_interaction_count"
                    ),

                    # MITRE ATLAS
                    "mitre_id": values.get(
                        "mitre_id"
                    ),

                    "mitre_tactic": values.get(
                        "mitre_tactic"
                    ),

                    "mitre_technique": values.get(
                        "mitre_technique"
                    )
                }

                events.append(event)

        return events

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    def close(self):
        self.client.close()