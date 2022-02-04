import csv
import os

import constants


def init_second_classifier():
    c = set()

    if os.path.exists(constants.CLASSIFIER_FILENAME):
        with open(
            constants.CLASSIFIER_FILENAME,
            "r",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            rows = csv.reader(f)
            for row in rows:
                if row[1] != constants.TOTAL_EXPENSE:
                    c.add(row[0])
        classifier_list = list(c)
        classifier_list.sort(key=lambda x: len(x))
        return classifier_list
    else:
        with open(
            constants.CLASSIFIER_FILENAME,
            "w",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    constants.SECOND_CLASSIFIER_EXAMPLE,
                    constants.FIRST_CLASSIFIER_EXAMPLE,
                ],
            )
            writer.writerow(
                [
                    constants.FIRST_CLASSIFIER_EXAMPLE,
                    constants.TOTAL_EXPENSE,
                ],
            )
            return [constants.SECOND_CLASSIFIER_EXAMPLE]


def init_first_classifier():
    if os.path.exists(constants.CLASSIFIER_FILENAME):
        c = set()
        with open(
            constants.CLASSIFIER_FILENAME,
            "r",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            rows = csv.reader(f)
            for row in rows:
                if row[1] == constants.TOTAL_EXPENSE:
                    c.add(row[0])
        classifier_list = list(c)
        classifier_list.sort(key=lambda x: len(x))
        return classifier_list
    else:
        with open(
            constants.CLASSIFIER_FILENAME,
            "w",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    constants.SECOND_CLASSIFIER_EXAMPLE,
                    constants.FIRST_CLASSIFIER_EXAMPLE,
                ],
            )
            writer.writerow(
                [
                    constants.FIRST_CLASSIFIER_EXAMPLE,
                    constants.TOTAL_EXPENSE,
                ],
            )
            return [constants.FIRST_CLASSIFIER_EXAMPLE]


def get_last_line():
    if os.path.exists(constants.SPENDING_FILENAME):
        last = []
        with open(
            constants.SPENDING_FILENAME,
            "r",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            reader = csv.reader(f)
            for row in reader:
                last = row
        return last
    else:
        with open(
            constants.SPENDING_FILENAME,
            "w",
            encoding=constants.ENCODING,
            newline="",
        ) as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    constants.EXAMPLE,
                    constants.SECOND_CLASSIFIER_EXAMPLE,
                    100,
                ],
            )
            return [
                constants.EXAMPLE,
                constants.SECOND_CLASSIFIER_EXAMPLE,
                100,
            ]


def write_spending(item, sort, price):
    from datetime import datetime

    month = datetime.now().month
    day = datetime.now().day
    item = f"{str(month)}.{str(day)}-{item}"
    with open(
        constants.SPENDING_FILENAME,
        "a",
        encoding=constants.ENCODING,
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow([item, sort, price])


def delete_last_line():
    lines = list()
    with open(
        constants.SPENDING_FILENAME,
        "r",
        encoding=constants.ENCODING,
        newline="",
    ) as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            lines.append(row)
    if not row:
        return 0
    with open(
        constants.SPENDING_FILENAME,
        "w",
        encoding=constants.ENCODING,
        newline="",
    ) as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines[:-1])
    return 1


def update_classifier(second, first):
    new_line = [second, first]
    with open(
        constants.CLASSIFIER_FILENAME,
        "r",
        encoding=constants.ENCODING,
        newline="",
    ) as f:
        rows = csv.reader(f)
        for row in rows:
            if second in row:
                return 0
    with open(
        constants.CLASSIFIER_FILENAME,
        "a",
        encoding=constants.ENCODING,
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow(new_line)
    return 1


def delete_classifier(items):
    exist = set()
    with open(
        constants.CLASSIFIER_FILENAME,
        "r",
        encoding=constants.ENCODING,
        newline="",
    ) as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            if row[0] in items or row[1] in items:
                exist.add(row[0])
                exist.add(row[1])

    with open(
        constants.SPENDING_FILENAME,
        "r",
        encoding=constants.ENCODING,
        newline="",
    ) as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            if row[1] in exist:
                return 0

    lines = list()
    with open(
        constants.CLASSIFIER_FILENAME,
        "r",
        encoding=constants.ENCODING,
        newline="",
    ) as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            if row[0] not in items and row[1] not in items:
                lines.append(row)

    with open(
        constants.CLASSIFIER_FILENAME,
        "w",
        encoding=constants.ENCODING,
        newline="",
    ) as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

    return 1
