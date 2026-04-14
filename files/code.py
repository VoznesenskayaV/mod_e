import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


OUTPUT_FILE = "data/attendance_data.csv"


def generate_attendance_csv():
    np.random.seed(42)

    groups = {
        "A-101": 0.88,
        "A-102": 0.84,
        "B-201": 0.80,
        "B-202": 0.76
    }

    subjects = {
        "Math": -0.02,
        "Physics": -0.05,
        "Informatics": 0.02,
        "Statistics": -0.01
    }

    students_by_group = {
        "A-101": [f"A101_{i:02d}" for i in range(1, 26)],
        "A-102": [f"A102_{i:02d}" for i in range(1, 26)],
        "B-201": [f"B201_{i:02d}" for i in range(1, 26)],
        "B-202": [f"B202_{i:02d}" for i in range(1, 26)],
    }

    start_date = datetime(2024, 9, 2)
    end_date = datetime(2024, 12, 27)

    rows = []
    event_id = 1
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:
            weekday_factor = {
                0: 0.02,
                1: 0.01,
                2: 0.00,
                3: -0.01,
                4: -0.03
            }[current_date.weekday()]

            semester_progress = (current_date - start_date).days / max((end_date - start_date).days, 1)
            trend_factor = -0.05 * semester_progress

            for group, base_attendance in groups.items():
                group_students = students_by_group[group]

                day_subjects = np.random.choice(list(subjects.keys()), size=2, replace=False)

                for subject_index, subject in enumerate(day_subjects):
                    subject_factor = subjects[subject]

                    for student in group_students:
                        noise = np.random.normal(0, 0.04)

                        prob_present = (
                            base_attendance
                            + weekday_factor
                            + trend_factor
                            + subject_factor
                            + noise
                        )

                        prob_present = max(0.55, min(0.98, prob_present))
                        present = int(np.random.rand() < prob_present)

                        event_time = current_date + timedelta(
                            hours=9 + subject_index * 2,
                            minutes=np.random.randint(0, 50),
                            seconds=np.random.randint(0, 60)
                        )

                        rows.append({
                            "event_id": f"E{event_id:06d}",
                            "time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "date": current_date.strftime("%Y-%m-%d"),
                            "group": group,
                            "student_id": student,
                            "subject": subject,
                            "present": present
                        })

                        event_id += 1

        current_date += timedelta(days=1)

    df = pd.DataFrame(rows)

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Файл сохранён: {OUTPUT_FILE}")
    print(f"Количество записей: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    generate_attendance_csv()
