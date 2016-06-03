import sys

from setuptools import setup, find_packages

from baseplate.integration.thrift.command import ThriftBuildPyCommand


PY3 = (sys.version_info.major == 3)

tests_require = [
    "nose",
    "coverage",
    "webtest",
]

if not PY3:
    tests_require.append("mock")

setup(
    name="reddit_service_ads_tracking",
    packages=find_packages(),
    install_requires=[
        "pyramid",
        "baseplate",
    ],
    cmdclass={
        "build_py": ThriftBuildPyCommand,
    },
    test_suite="tests",
    tests_require=tests_require,
)
