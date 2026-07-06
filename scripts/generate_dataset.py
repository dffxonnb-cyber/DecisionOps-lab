"""Generate a reproducible synthetic product event dataset for DecisionOps Lab.

Outputs:
- data/raw/raw_users.csv
- data/raw/raw_events.csv
- data/raw/raw_sessions.csv
- data/raw/raw_experiments.csv
- data/raw/raw_payments.csv
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from uuid import NAMESPACE_DNS, uuid5

import numpy as np
import pandas as pd


SCENARIOS: dict[str, dict[str, Any]] = {
    "strong_positive": {
        "seed_offset": 0,
        "variant_b_activation_lift": 0.055,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 0,
    },
    "guardrail_risk": {
        "seed_offset": 101,
        "variant_b_activation_lift": 0.055,
        "variant_b_revisit_adjustment": -0.12,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 0,
    },
    "refund_risk": {
        "seed_offset": 505,
        "variant_b_activation_lift": 0.055,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.55,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 0,
    },
    "session_activity_risk": {
        "seed_offset": 606,
        "variant_b_activation_lift": 0.055,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": -0.10,
        "invalid_variant_rows": 0,
    },
    "weak_evidence": {
        "seed_offset": 202,
        "variant_b_activation_lift": 0.012,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 0,
    },
    "neutral": {
        "seed_offset": 303,
        "variant_b_activation_lift": -0.010,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 0,
    },
    "quality_failure": {
        "seed_offset": 404,
        "variant_b_activation_lift": 0.055,
        "variant_b_revisit_adjustment": 0.00,
        "variant_b_refund_adjustment": 0.00,
        "variant_b_session_activity_adjustment": 0.00,
        "invalid_variant_rows": 25,
    },
}


@dataclass(frozen=True)
class DatasetConfig:
    seed: int = 20260703
    user_count: int = 10_000
    start_date: str = "2026-01-01"
    end_date: str = "2026-03-31"
    experiment_name: str = "onboarding_v2"
    scenario: str = "strong_positive"

    @property
    def scenario_config(self) -> dict[str, Any]:
        return SCENARIOS[self.scenario]

    @property
    def scenario_seed(self) -> int:
        return self.seed + int(self.scenario_config["seed_offset"])


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"


def stable_id(prefix: str, *parts: object) -> str:
    key = "|".join(str(part) for part in parts)
    return f"{prefix}_{uuid5(NAMESPACE_DNS, key).hex[:16]}"


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def random_datetimes(rng: np.random.Generator, start: str, end: str, size: int) -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    seconds = int((end_ts - start_ts).total_seconds())
    offsets = rng.integers(0, seconds, size=size)
    return pd.Series(start_ts + pd.to_timedelta(offsets, unit="s"))


def create_users(config: DatasetConfig, rng: np.random.Generator) -> pd.DataFrame:
    user_ids = [f"user_{idx:05d}" for idx in range(1, config.user_count + 1)]

    users = pd.DataFrame(
        {
            "user_id": user_ids,
            "signup_at": random_datetimes(rng, config.start_date, config.end_date, config.user_count).dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "acquisition_channel": rng.choice(
                ["organic", "paid_search", "social", "referral"],
                size=config.user_count,
                p=[0.43, 0.25, 0.22, 0.10],
            ),
            "device_type": rng.choice(
                ["mobile", "desktop", "tablet"],
                size=config.user_count,
                p=[0.68, 0.24, 0.08],
            ),
            "age_group": rng.choice(
                ["10s", "20s", "30s", "40s+"],
                size=config.user_count,
                p=[0.16, 0.44, 0.28, 0.12],
            ),
        }
    ).sort_values("signup_at", ignore_index=True)

    return users


def create_experiments(config: DatasetConfig, users: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    experiments = users[["user_id", "signup_at"]].copy()
    experiments["experiment_name"] = config.experiment_name
    experiments["variant"] = rng.choice(["A", "B"], size=len(users), p=[0.50, 0.50])
    experiments["assigned_at"] = experiments["signup_at"]
    experiments["scenario"] = config.scenario

    invalid_variant_rows = int(config.scenario_config.get("invalid_variant_rows", 0))
    if invalid_variant_rows > 0:
        experiments.loc[experiments.index[:invalid_variant_rows], "variant"] = "C"

    return experiments[["user_id", "experiment_name", "variant", "assigned_at", "scenario"]]


def probability_adjustment(users: pd.DataFrame, experiments: pd.DataFrame, config: DatasetConfig) -> pd.Series:
    base = pd.Series(0.34, index=users.index, dtype="float64")

    base += np.where(users["device_type"].eq("mobile"), 0.03, 0.00)
    base += np.where(users["device_type"].eq("desktop"), 0.01, 0.00)
    base += np.where(users["acquisition_channel"].eq("organic"), 0.04, 0.00)
    base += np.where(users["acquisition_channel"].eq("referral"), 0.05, 0.00)
    base -= np.where(users["acquisition_channel"].eq("paid_search"), 0.03, 0.00)
    base += np.where(users["age_group"].eq("20s"), 0.02, 0.00)
    base -= np.where(users["age_group"].eq("40s+"), 0.02, 0.00)

    lift = float(config.scenario_config["variant_b_activation_lift"])
    base += np.where(experiments["variant"].eq("B"), lift, 0.00)

    return base.clip(0.05, 0.85)


def add_event(
    records: list[dict[str, object]],
    user_id: str,
    session_id: str,
    event_name: str,
    event_time: pd.Timestamp,
    sequence: int,
) -> None:
    records.append(
        {
            "event_id": stable_id("event", user_id, session_id, event_name, sequence, event_time),
            "user_id": user_id,
            "session_id": session_id,
            "event_name": event_name,
            "event_time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "event_sequence": sequence,
        }
    )


def create_events_and_sessions(
    config: DatasetConfig,
    users: pd.DataFrame,
    experiments: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    events: list[dict[str, object]] = []
    sessions: list[dict[str, object]] = []

    users_reset = users.reset_index(drop=True)
    experiments_reset = experiments.reset_index(drop=True)
    activation_p = probability_adjustment(users_reset, experiments_reset, config)
    variant_by_user = dict(zip(experiments_reset["user_id"], experiments_reset["variant"], strict=True))
    revisit_shift = float(config.scenario_config["variant_b_revisit_adjustment"])
    session_activity_shift = float(config.scenario_config.get("variant_b_session_activity_adjustment", 0.00))

    for idx, user in users_reset.iterrows():
        user_id = str(user["user_id"])
        signup_at = pd.Timestamp(user["signup_at"])
        device_type = str(user["device_type"])
        variant = variant_by_user[user_id]

        session_id = stable_id("session", user_id, "signup")
        sequence = 1

        add_event(events, user_id, session_id, "signup", signup_at, sequence)
        sequence += 1

        onboarding_start = signup_at + pd.to_timedelta(int(rng.integers(30, 600)), unit="s")
        add_event(events, user_id, session_id, "onboarding_start", onboarding_start, sequence)
        sequence += 1

        onboarding_completed = rng.random() < 0.78
        activated = False

        if onboarding_completed:
            onboarding_complete = onboarding_start + pd.to_timedelta(int(rng.integers(120, 1800)), unit="s")
            add_event(events, user_id, session_id, "onboarding_complete", onboarding_complete, sequence)
            sequence += 1

            activated = rng.random() < float(activation_p.iloc[idx])
            if activated:
                created_at = onboarding_complete + pd.to_timedelta(int(rng.integers(60, 20 * 3600)), unit="s")
                add_event(events, user_id, session_id, "create_routine", created_at, sequence)
                sequence += 1

                if rng.random() < 0.72:
                    complete_at = created_at + pd.to_timedelta(int(rng.integers(3600, 36 * 3600)), unit="s")
                    add_event(events, user_id, session_id, "complete_routine", complete_at, sequence)
                    sequence += 1

        session_end = signup_at + pd.to_timedelta(int(rng.integers(600, 3600)), unit="s")
        sessions.append(
            {
                "session_id": session_id,
                "user_id": user_id,
                "session_start": signup_at.strftime("%Y-%m-%d %H:%M:%S"),
                "session_end": session_end.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": int((session_end - signup_at).total_seconds()),
                "device_type": device_type,
                "session_type": "signup",
            }
        )

        return_probability = 0.47 if activated else 0.23
        if variant == "B":
            return_probability += revisit_shift
        return_probability = float(np.clip(return_probability, 0.02, 0.80))

        for day in [1, 3, 7, 14]:
            day_weight = 0.92 if day == 1 else 0.75 if day == 3 else 0.58 if day == 7 else 0.40
            day_return_probability = return_probability
            if variant == "B" and day != 7:
                day_return_probability += session_activity_shift
            day_return_probability = float(np.clip(day_return_probability, 0.02, 0.80))

            if rng.random() < day_return_probability * day_weight:
                visit_time = signup_at + pd.Timedelta(days=day) + pd.to_timedelta(
                    int(rng.integers(0, 24 * 3600)), unit="s"
                )
                return_session_id = stable_id("session", user_id, f"return_{day}")
                duration_seconds = int(rng.integers(300, 2400))
                add_event(events, user_id, return_session_id, "return_visit", visit_time, 1)
                sessions.append(
                    {
                        "session_id": return_session_id,
                        "user_id": user_id,
                        "session_start": visit_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "session_end": (visit_time + pd.to_timedelta(duration_seconds, unit="s")).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "duration_seconds": duration_seconds,
                        "device_type": device_type,
                        "session_type": f"return_d{day}",
                    }
                )

    events_df = pd.DataFrame(events).sort_values(["user_id", "event_time", "event_sequence"], ignore_index=True)
    sessions_df = pd.DataFrame(sessions).sort_values(["user_id", "session_start"], ignore_index=True)

    return events_df, sessions_df


def create_payments(
    config: DatasetConfig,
    users: pd.DataFrame,
    events: pd.DataFrame,
    experiments: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    routine_users = set(events.loc[events["event_name"].eq("create_routine"), "user_id"])
    variant_by_user = dict(zip(experiments["user_id"], experiments["variant"], strict=True))
    refund_adjustment = float(config.scenario_config.get("variant_b_refund_adjustment", 0.00))
    records: list[dict[str, object]] = []

    for user in users.itertuples(index=False):
        user_id = str(user.user_id)
        signup_at = pd.Timestamp(user.signup_at)
        variant = str(variant_by_user.get(user_id, "unknown"))

        if user_id not in routine_users:
            continue

        if rng.random() < 0.22:
            trial_time = signup_at + pd.to_timedelta(int(rng.integers(1, 10)), unit="D")
            records.append(
                {
                    "payment_id": stable_id("payment", user_id, "trial"),
                    "user_id": user_id,
                    "payment_status": "trial_start",
                    "payment_time": trial_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "amount": 0,
                }
            )

            if rng.random() < 0.42:
                paid_time = trial_time + pd.to_timedelta(int(rng.integers(7, 15)), unit="D")
                amount = int(rng.choice([5900, 9900, 12900], p=[0.45, 0.40, 0.15]))
                records.append(
                    {
                        "payment_id": stable_id("payment", user_id, "paid"),
                        "user_id": user_id,
                        "payment_status": "paid_conversion",
                        "payment_time": paid_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "amount": amount,
                    }
                )

                refund_probability = 0.045
                if variant == "B":
                    refund_probability += refund_adjustment
                refund_probability = float(np.clip(refund_probability, 0.00, 0.80))

                if rng.random() < refund_probability:
                    refund_time = paid_time + pd.to_timedelta(int(rng.integers(1, 7)), unit="D")
                    records.append(
                        {
                            "payment_id": stable_id("payment", user_id, "refund"),
                            "user_id": user_id,
                            "payment_status": "refund",
                            "payment_time": refund_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "amount": -amount,
                        }
                    )

    return pd.DataFrame(records).sort_values(["user_id", "payment_time"], ignore_index=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8")


def print_counts(config: DatasetConfig, tables: Iterable[tuple[str, pd.DataFrame]]) -> None:
    print("\nGenerated raw dataset")
    print("-" * 48)
    print(f"scenario                 {config.scenario}")
    for name, df in tables:
        print(f"{name:<24} {len(df):>8,} rows")
    print("-" * 48)
    print(f"Output directory: {RAW_DIR.relative_to(ROOT_DIR)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic product event data.")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        default="strong_positive",
        help="Synthetic scenario to generate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = DatasetConfig(scenario=args.scenario)
    rng = np.random.default_rng(config.scenario_seed)
    ensure_dirs()

    users = create_users(config, rng)
    experiments = create_experiments(config, users, rng)
    events, sessions = create_events_and_sessions(config, users, experiments, rng)
    payments = create_payments(config, users, events, experiments, rng)

    write_csv(users, RAW_DIR / "raw_users.csv")
    write_csv(events, RAW_DIR / "raw_events.csv")
    write_csv(sessions, RAW_DIR / "raw_sessions.csv")
    write_csv(experiments, RAW_DIR / "raw_experiments.csv")
    write_csv(payments, RAW_DIR / "raw_payments.csv")

    print_counts(
        config,
        [
            ("raw_users.csv", users),
            ("raw_events.csv", events),
            ("raw_sessions.csv", sessions),
            ("raw_experiments.csv", experiments),
            ("raw_payments.csv", payments),
        ],
    )


if __name__ == "__main__":
    main()
