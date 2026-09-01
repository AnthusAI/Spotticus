Feature: Target Filtering and Lock Management
  To minimize context window usage for autonomous agents and prevent
  collisions, Spotticus allows surgical querying and exclusive locking
  of individual model pools.

  Scenario: Filtering by specific targets
    Given Spotticus supports providers "antigravity", "cursor", and "claude"
    When an agent runs status for target "cursor.premium"
    Then the probe only queries the "cursor" API
    And the output strictly contains the "cursor.premium" pool

  Scenario: Claiming and releasing a pool lock
    Given the "antigravity.gemini" pool is eligible
    When an agent claims "antigravity.gemini" with PID 123
    Then a lockfile is created for "antigravity.gemini"
    And the pool is marked as "Locked"
    When the agent releases "antigravity.gemini" with PID 123
    Then the lockfile is removed
