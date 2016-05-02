Feature: Check for config file in default location
    
    Scenario: config file existence check
        Given creating a new profile (using quickstart)
        When  new config file created in default or user-given location
        Then  detect any existing config before creating new config