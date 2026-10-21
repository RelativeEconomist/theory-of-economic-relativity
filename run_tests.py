import sys
import unittest
from pathlib import Path


class FriendlyTestResult(unittest.TextTestResult):
    """Human readable TER test output."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_group = None
        self.current_failed = False
        self.failed_tests = 0

    def startTest(self, test):
        super().startTest(test)
        self.current_failed = False

        group = test.__class__.__name__
        if group != self.current_group:
            self.current_group = group

            title = getattr(
                test.__class__,
                "TEST_NAME",
                group.replace("Test", "").replace("_", " "),
            )

            self.stream.writeln()
            self.stream.writeln(f"{title}")

    def _friendly_name(self, test):
        name = test._testMethodName
        name = name.removeprefix("test_")
        return name.replace("_", " ").capitalize()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.current_failed = True

    def addError(self, test, err):
        super().addError(test, err)
        self.current_failed = True

    def addSubTest(self, test, subtest, err):
        # A failing subtest marks its whole test failed; unittest does not
        # call addSuccess for that test.
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.current_failed = True

    def stopTest(self, test):
        super().stopTest(test)
        if self.current_failed:
            self.failed_tests += 1
            self.stream.writeln(f"  ✗ {self._friendly_name(test)}")
        else:
            self.stream.writeln(f"  ✓ {self._friendly_name(test)}")


class FriendlyTestRunner(unittest.TextTestRunner):
    resultclass = FriendlyTestResult


def main():
    repo_root = Path(__file__).resolve().parent
    test_dirs = [
        repo_root / "research" / "tests",
        repo_root / "research" / "reproductions",
    ]

    # Optional: run a single test file, e.g.
    # python3 run_tests.py research/tests/test_27_pokemon_card_choice.py
    pattern = "test_*.py"
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
        test_dirs = [
            test_dir
            for test_dir in test_dirs
            if (test_dir / test_file.name).is_file()
        ]
        if not test_dirs:
            raise SystemExit(
                "Test file not found in research/tests or "
                f"research/reproductions: {sys.argv[1]}"
            )
        pattern = test_file.name

    suite = unittest.TestSuite(
        unittest.defaultTestLoader.discover(
            start_dir=str(test_dir),
            pattern=pattern,
            top_level_dir=str(repo_root),
        )
        for test_dir in test_dirs
    )

    print()
    print("Theory of Economic Relativity")
    print("Academic Replication Test Suite")
    print("=" * 44)

    runner = FriendlyTestRunner(
        verbosity=0,
        stream=sys.stdout,
    )

    result = runner.run(suite)

    print()
    print("=" * 44)

    if result.testsRun == 0:
        print("FAIL: no tests were discovered.")
        raise SystemExit(1)

    if result.wasSuccessful():
        print(
            f"PASS: {result.testsRun} tests completed successfully."
        )
    else:
        failures = len(result.failures)
        errors = len(result.errors)

        # failures and errors count each failing subtest separately.
        print(
            f"FAIL: {result.failed_tests} of {result.testsRun} tests failed "
            f"({failures} failures, {errors} errors, counting subtests)."
        )

    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()