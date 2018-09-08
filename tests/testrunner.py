"""
Modified from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/appengine/standard/localtesting/runner.py
"""
import argparse
import os
import re
import sys
import unittest


def fixup_paths(path):
    """Adds GAE SDK path to system path and appends it to the google path
    if that already exists."""
    # Not all Google packages are inside namespace packages, which means
    # there might be another non-namespace package named `google` already on
    # the path and simply appending the App Engine SDK to the path will not
    # work since the other package will get discovered and used first.
    # This emulates namespace packages by first searching if a `google` package
    # exists by importing it, and if so appending to its module search path.
    try:
        import google
        google.__path__.append("{0}/google".format(path))
    except ImportError:
        pass

    sys.path.insert(0, path)

def find_google_sdk_path():
    """Go through the PATH environment variable and parse out gcloudsdk path.

    We don't know where the path is and I'm too lazy to type it out manually
    And the paths are different on my chromebook and desktop VM so we gotta
    get the path dynamically.
    """
    reg = r'.*\{0}(.*google-cloud-sdk\{1}).*'.format(os.pathsep, os.sep)
    res = re.match(reg, os.environ['PATH']).groups()[0]
    print 'Found SDK path: ' + res
    return res

def main(test_path, test_pattern):
    sdk_path = find_google_sdk_path()

    # If the SDK path points to a Google Cloud SDK installation
    # then we should alter it to point to the GAE platform location.
    if os.path.exists(os.path.join(sdk_path, 'platform/google_appengine')):
        sdk_path = os.path.join(sdk_path, 'platform/google_appengine')

    # Make sure google.appengine.* modules are importable.
    fixup_paths(sdk_path)

    # Make sure all bundled third-party packages are available.
    import dev_appserver
    dev_appserver.fix_sys_path()

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
        import appengine_config
        (appengine_config)
    except ImportError:
        print('Note: unable to import appengine_config.')

    # Discover and run tests.
    suite = unittest.loader.TestLoader().discover(test_path, test_pattern)
    return unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--test-path',
        help='The path to look for tests, defaults to the current directory.',
        default=os.getcwd())
    parser.add_argument(
        '--test-pattern',
        help='The file pattern for test modules, defaults to *_tests.py.',
        default='*_tests.py')

    args = parser.parse_args()

    result = main(args.test_path, args.test_pattern)