Feature: Kanbus Spot Task Routing
  Kanbus tasks are tagged with composite labels and sorted by
  priority and creation time to route work to the correct background agent.

  Scenario: Routing a task to a specific model pool
    Given a Kanbus task is labeled "spot:antigravity.gemini"
    When the Antigravity spot worker searches for "spot:antigravity.gemini" tasks
    Then the task is found
    When the Cursor spot worker searches for "spot:cursor" tasks
    Then the task is not found

  Scenario: Prioritizing the spot backlog
    Given the following tasks are labeled "spot:cursor":
      | Task | Priority |
      | A    | 2        |
      | B    | 1        |
      | C    | 2        |
    When the agent sorts by priority
    Then the tasks are returned in the order "B", "A", "C"
