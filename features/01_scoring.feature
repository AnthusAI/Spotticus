Feature: Spare Capacity Scoring and Multi-Tank Pools
  To ensure interactive work is never blocked by background tasks,
  Spotticus evaluates leftover quota against a linear pace of time,
  and treats independent model tiers (tanks) as separate resources.

  Scenario: Window is half elapsed with low usage
    Given a quota window that resets in 10080 minutes
    And 5040 minutes have elapsed since reset
    And the used quota percent is 20.0
    When Spotticus computes the spare-pace score
    Then the spare score is 0.30
    And the window is considered spare

  Scenario: Independent model tanks in a single provider
    Given the Antigravity provider has a "gemini" pool and a "claude" pool
    And the "claude" pool is 99% depleted
    And the "gemini" pool is 20% depleted with 50% time elapsed
    When Spotticus evaluates the "antigravity" provider
    Then the "antigravity.claude" pool is scored as "SKIP"
    And the "antigravity.gemini" pool is scored as "ELIGIBLE"
