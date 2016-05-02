Feature: create directory for twtxt file if given dir does not exist
    

    Scenario: create twtxt dir (os-independent)
        Given creating new profile (using quickstart)
        When create new twtxt file in a non-existent directory
        Then the specified directory is created
		
		