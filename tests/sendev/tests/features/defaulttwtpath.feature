Feature: function without error using quickstart if the --config doesn't exist
    

    Scenario: create twtxt dir (os-independent)
        Given I am creating a new profile (using quickstart)
        When create a new config file in a non-existent directory
        Then create the specified directory and place config there