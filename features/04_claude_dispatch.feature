Feature: Claude Code spot dispatch
  The Claude trigger dispatches a headless worker onto leftover claude quota only when
  the pool is genuinely spare, and it never leaves the pool wedged or a chore stranded.

  Scenario: A pool that is not spare is not dispatched
    Given the "claude.spectest" pool is not spare
    When the Claude spot trigger runs
    Then the trigger declines to dispatch
    And the Claude CLI is not invoked
    And no lock remains for "claude.spectest"

  Scenario: A failed probe is not dispatched
    Given the leftover probe fails
    When the Claude spot trigger runs
    Then the trigger declines to dispatch
    And the Claude CLI is not invoked
    And no lock remains for "claude.spectest"

  Scenario: A spare pool dispatches a headless worker
    Given the "claude.spectest" pool is spare
    When the Claude spot trigger runs
    Then the Claude CLI is invoked in non-interactive mode
    And the worker prompt contains the Claude spot worker skill
    And no lock remains for "claude.spectest"

  Scenario: A pool already running a spot job is not dispatched twice
    Given the "claude.spectest" pool is spare
    And the pool is already locked by another agent
    When the Claude spot trigger runs
    Then the trigger declines to dispatch
    And the Claude CLI is not invoked

  Scenario: A failed worker still releases the pool
    Given the "claude.spectest" pool is spare
    And the Claude CLI will exit with a failure
    And the worker has claimed a Kanbus chore
    When the Claude spot trigger runs
    Then no lock remains for "claude.spectest"
    And the claimed Kanbus chore is reopened

  Scenario: A worker that overruns its cap is terminated
    Given the "claude.spectest" pool is spare
    And the Claude CLI will hang
    And the worker has claimed a Kanbus chore
    And the run cap is 1 second
    When the Claude spot trigger runs
    Then the trigger terminates the worker
    And no lock remains for "claude.spectest"
    And the claimed Kanbus chore is reopened

  Scenario: An on-demand hold preempts a running spot job
    Given the "claude.spectest" pool is spare
    And the Claude CLI will hang
    And the worker has claimed a Kanbus chore
    When the Claude spot trigger runs and the pool is held
    Then the trigger terminates the worker
    And the lock for "claude.spectest" remains HELD
    And the claimed Kanbus chore is reopened
