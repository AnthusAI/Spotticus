Feature: Model Classes and Routing
  To dispatch tasks to the best available provider,
  Spotticus uses a local configuration defining classes of models,
  and resolves the best app based on quota availability.

  Scenario: Resolving a class with the first app eligible
    Given a local configuration file with a "cheap" class:
      | app         | model            | thinking |
      | antigravity | gemini-3.8-flash | high     |
      | cursor      | grok             | normal   |
    And the "antigravity.gemini" routing pool is eligible
    And the "cursor.grok" routing pool is eligible
    When Spotticus resolves the "cheap" class
    Then it returns the "antigravity" app
    And it returns the "gemini-3.8-flash" model

  Scenario: Resolving a class falling back to the second app
    Given a local configuration file with a "cheap" class:
      | app         | model            |
      | antigravity | gemini-3.8-flash |
      | cursor      | grok             |
    And the "antigravity.gemini" routing pool is NOT eligible
    And the "cursor.grok" routing pool is eligible
    When Spotticus resolves the "cheap" class
    Then it returns the "cursor" app
    And it returns the "grok" model

  Scenario: Resolving a specific app overriding the class order
    Given a local configuration file with a "cheap" class:
      | app         | model            |
      | antigravity | gemini-3.8-flash |
      | cursor      | grok             |
    And the "antigravity.gemini" routing pool is eligible
    And the "cursor.grok" routing pool is eligible
    When Spotticus resolves the "cheap" class explicitly for the "cursor" app
    Then it returns the "cursor" app
    And it returns the "grok" model

  Scenario: Resolving a class with no apps eligible
    Given a local configuration file with a "cheap" class:
      | app         | model            |
      | antigravity | gemini-3.8-flash |
      | cursor      | grok             |
    And the "antigravity.gemini" routing pool is NOT eligible
    And the "cursor.grok" routing pool is NOT eligible
    When Spotticus resolves the "cheap" class
    Then it returns an error indicating no eligible apps
