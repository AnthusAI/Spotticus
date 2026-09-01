Feature: Cursor Composer spot dispatch
  Spare Cursor Models quota is claimed by a cron wrapper that launches
  a headless Composer 2.5 agent with the composer-spot-worker skill.

  Scenario: Eligible pool launches Composer with the worker skill
    Given the Cursor CLI agent is on PATH
    And the "cursor.cursor-models" pool is eligible
    When the Cursor dispatch wrapper runs
    Then a lock is claimed for "cursor.cursor-models"
    And the Cursor CLI is invoked with print mode, model "composer-2.5", and trust
    And the lock for "cursor.cursor-models" is released

  Scenario: Missing Cursor CLI fails closed
    Given the Cursor CLI agent is not on PATH
    And the "cursor.cursor-models" pool is eligible
    When the Cursor dispatch wrapper runs
    Then no lock is claimed
    And the Cursor CLI is not invoked

  Scenario: Ineligible pool does not dispatch
    Given the Cursor CLI agent is on PATH
    And the "cursor.cursor-models" pool is not eligible
    When the Cursor dispatch wrapper runs
    Then no lock is claimed
    And the Cursor CLI is not invoked
