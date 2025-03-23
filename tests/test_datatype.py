# ruff: noqa: S101, E501, ANN201
import pytest

from ruff_report.datatype import Location, Violation, ViolationList


@pytest.mark.parametrize(
    ("json_text", "expected"),
    [
        pytest.param(
            """
          {
            "cell": null,
            "code": null,
            "end_location": {
              "column": 1,
              "row": 10
            },
            "filename": "/sample_project/sample.py",
            "fix": null,
            "location": {
              "column": 28,
              "row": 9
            },
            "message": "SyntaxError: Expected an indented block after function definition",
            "noqa_row": null,
            "url": null
          }
        """,
            Violation(
                cell=None,
                code=None,
                location=Location(row=9, column=28),
                end_location=Location(row=10, column=1),
                filename="/sample_project/sample.py",
                message="SyntaxError: Expected an indented block after function definition",
                noqa_row=None,
                url=None,
                fix=None,
            ),
            id="Simple",
        )
    ],
)
def test_violation_from_jsontext(json_text: str, expected: Violation):
    actual = Violation.model_validate_json(json_text)
    assert actual == expected


@pytest.mark.parametrize(
    ("json_text_list", "expected"),
    [
        pytest.param(
            """
        [
          {
            "cell": null,
            "code": "COM812",
            "end_location": {
              "column": 6,
              "row": 7
            },
            "filename": "/sample_project/sample1.py",
            "fix": null,
            "location": {
              "column": 6,
              "row": 7
            },
            "message": "Trailing comma missing",
            "noqa_row": 7,
            "url": "https://docs.astral.sh/ruff/rules/missing-trailing-comma"
          },
          {
            "cell": null,
            "code": null,
            "end_location": {
              "column": 1,
              "row": 10
            },
            "filename": "/sample_project/sample2.py",
            "fix": null,
            "location": {
              "column": 28,
              "row": 9
            },
            "message": "SyntaxError: Expected an indented block after function definition",
            "noqa_row": null,
            "url": null
          }
        ]
        """,
            ViolationList(
                [
                    Violation(
                        cell=None,
                        code="COM812",
                        location=Location(row=7, column=6),
                        end_location=Location(row=7, column=6),
                        filename="/sample_project/sample1.py",
                        message="Trailing comma missing",
                        noqa_row=7,
                        url="https://docs.astral.sh/ruff/rules/missing-trailing-comma",
                        fix=None,
                    ),
                    Violation(
                        cell=None,
                        code=None,
                        location=Location(row=9, column=28),
                        end_location=Location(row=10, column=1),
                        filename="/sample_project/sample2.py",
                        message="SyntaxError: Expected an indented block after function definition",
                        noqa_row=None,
                        url=None,
                        fix=None,
                    ),
                ]
            ),
            id="Simple",
        )
    ],
)
def test_violations_from_jsontext(json_text_list: str, expected: ViolationList):
    actual = ViolationList.model_validate_json(json_text_list)
    assert actual == expected

