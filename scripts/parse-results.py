#!/bin/env python3
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from junitparser import JUnitXml, Failure, Error, Skipped

err_console = Console(stderr=True)
console = Console()

failed_table = Table(show_lines=True)
errored_table = Table(show_lines=True)
skipped_table = Table(show_lines=True)


def get_api_docs_url(test_xml_name, name):
    return f'https://cite.opengeospatial.org/te2/about/ogcapi-tiles-1.0/1.0/site/apidocs/index.html?{test_xml_name.replace(".","/")}.html ({name})'


def add_table(table, tuples, title):
    table.add_column(
        "Case Name", justify="right", style="cyan", no_wrap=False, overflow="fold"
    )
    table.add_column(
        "Error", justify="right", style="red", no_wrap=False, overflow="fold"
    )
    table.add_column(
        "File", justify="right", style="magenta", no_wrap=False, overflow="fold"
    )
    table.add_column(
        "Url", justify="right", style="orange1", no_wrap=False, overflow="fold"
    )
    for case in tuples:
        table.add_row(case[1], case[2], str(case[0]), case[3])

    table.title = title
    console.print(table)


def main(result_dir, service_url, pretty_print, exit_on_fail):
    """
    Parse junit result.
    """

    failed_cases = []
    failed_tuples = []

    skipped_cases = []
    skipped_tuples = []

    errored_cases = []
    errored_tuples = []

    dir_path = Path(args.result_dir)
    for junit_test in dir_path.glob("**/**/TEST-org.opengis.cite.*.xml"):
        test_xml = JUnitXml.fromfile(str(junit_test))

        failed = [
            case
            for case in test_xml
            if any(isinstance(item, Failure) for item in case.result)
        ]
        failed_message = [result.message for fail in failed for result in fail.result]
        failed_tuples += [
            (
                junit_test.name,
                test_xml.name,
                result.message,
                get_api_docs_url(test_xml.name, fail.name),
            )
            for fail in failed
            for result in fail.result
        ]
        if failed:
            fail_name = next(iter([fail.name for fail in failed]), "")
            failed_cases += (
                [f"## {test_xml.name}"]
                + [""]
                + failed_message
                + [""]
                + [get_api_docs_url(test_xml.name, fail_name)]
                + [""]
            )

        skipped = [
            case
            for case in test_xml
            if any(isinstance(item, Skipped) for item in case.result)
        ]
        errored_or_skipped = [
            case
            for case in test_xml
            if any(isinstance(item, Error) for item in case.result)
        ]
        if errored_or_skipped:
            for case in errored_or_skipped:
                # TestNG SkipExceptions are wrongfully marked as errored when using the JUnit reporter.
                # Turn these errored tests into skipped tests.
                if case.result[0].type == 'org.testng.SkipException':
                    skipped += [case]
                else:
                    # Not a SkipException so treat as errored
                    errored = [case]
                    errored_message = [
                        result.message for error in errored for result in error.result
                    ]
                    errored_tuples += [
                        (
                            junit_test.name,
                            test_xml.name,
                            result.message,
                            get_api_docs_url(test_xml.name, error.name),
                        )
                        for error in errored
                        for result in error.result
                    ]
                    if errored:
                        error_name = next(iter([error.name for error in errored]), "")
                        errored_cases += (
                            [f"## {test_xml.name}"]
                            + errored_message
                            + [""]
                            + [get_api_docs_url(test_xml.name, error_name)]
                            + [""]
                        )

        # Handle skipped
        skipped_message = [result.message for skip in skipped for result in skip.result]
        skipped_tuples += [
            (
                junit_test.name,
                test_xml.name,
                result.message,
                get_api_docs_url(test_xml.name, skip.name),
            )
            for skip in skipped
            for result in skip.result
        ]
        if skipped:
            skip_name = next(iter([skip.name for skip in skipped]), "")
            skipped_cases += (
                    [f"## {test_xml.name}"]
                    + skipped_message
                    + [""]
                    + [get_api_docs_url(test_xml.name, skip_name)]
                    + [""]
            )

    if pretty_print:
        console.print(
            "ogcapi-tiles-1.0-1.1 Test Suite Run",
            style="bold italic underline",
            justify="center",
        )
        console.print("\n")
        console.print(f"Output test run saved in: '{result_dir}'", justify="center")
        if service_url:
            console.print(f"Test instance: '{service_url}'", justify="center")
        console.print("\n")

        if failed_tuples:
            add_table(
                failed_table, failed_tuples, f"FAILED TEST CASES ({len(failed_tuples)})"
            )

        if errored_tuples:
            add_table(
                errored_table,
                errored_tuples,
                f"ERRORED TEST CASES ({len(errored_tuples)})",
            )

        if skipped_tuples:
            add_table(
                skipped_table,
                skipped_tuples,
                f"SKIPPED TEST CASES ({len(skipped_tuples)})",
            )

    else:
        console.print("# ogcapi-tiles-1.0-1.1 Test Suite Run\n")
        console.print(f"- Output test run saved in: '{result_dir}'")
        if service_url:
            console.print(f"- Test instance: '{service_url}'")
        console.print("\n")

        if failed_cases:
            console.print("# FAILED TEST CASES\n", style="red")
            console.print("\n".join(failed_cases), style="red")

        if errored_cases:
            console.print("# ERRORED TEST CASES\n", style="orange1")
            console.print("\n".join(errored_cases), style="orange1")

        if skipped_cases:
            console.print("# SKIPPED TEST CASES\n", style="yellow")
            console.print("\n".join(skipped_cases), style="yellow")

    if failed_cases and exit_on_fail:
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse OAF ETS results")
    parser.add_argument(
        "result_dir", type=str, help="Directory with the result to parse"
    )
    parser.add_argument(
        "--service-url", help="Optional service url to print to console"
    )
    parser.add_argument(
        "--pretty-print", action="store_true", help="Print with a better formatting"
    )
    parser.add_argument(
        "--exit-on-fail",
        action="store_true",
        help="Force failing with exit code 1 when failed tests cases in result",
    )
    args = parser.parse_args()

    dir_path = Path(args.result_dir)
    if not dir_path.exists():
        err_console.print(f"test dir '{args.result_dir}' should exist")
        exit(1)

    main(args.result_dir, args.service_url, args.pretty_print, args.exit_on_fail)
