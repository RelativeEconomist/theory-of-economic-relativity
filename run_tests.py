import sys
import unittest
from pathlib import Path


class FriendlyTestResult(unittest.TextTestResult):
    """Human readable TER test output."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_group = None

    def startTest(self, test):
        super().startTest(test)

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

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln(f"  ✓ {self._friendly_name(test)}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.writeln(f"  ✗ {self._friendly_name(test)}")

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.writeln(f"  ✗ {self._friendly_name(test)}")


class FriendlyTestRunner(unittest.TextTestRunner):
    resultclass = FriendlyTestResult


def main():
    repo_root = Path(__file__).resolve().parent
    tests_dir = repo_root / "research" / "tests"

    suite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(repo_root),
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

    if result.wasSuccessful():
        print(
            f"PASS: {result.testsRun} tests completed successfully."
        )
    else:
        failed = len(result.failures)
        errors = len(result.errors)

        print(
            f"FAIL: {result.testsRun} tests run, "
            f"{failed} failures, {errors} errors."
        )

    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()