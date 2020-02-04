from pmc.restapi-client import demo_function


def test_demo_function():
    """
    Test ``pmc.restapi-client.demo_function(int)`` functionality.
    """
    assert demo_function(1) == 1
