Feature: Spotticus SDK dispatch
  Spotticus can drive the worker in-process through the Claude Agent SDK instead of shelling
  out to the CLI. The dispatch contract is the same one the shell trigger honours; what the
  SDK adds is a real turn ceiling and the ability to stop a run between messages.

  Scenario: A pool at pace is not dispatched
    Given the leftover probe reports the claude pool is at pace
    When the SDK spot trigger runs
    Then the agent SDK is not called
    And no lock remains for the claude pool

  Scenario: A probe that fails is not dispatched
    Given the leftover probe fails for the claude pool
    When the SDK spot trigger runs
    Then the agent SDK is not called
    And no lock remains for the claude pool

  Scenario: A spare pool runs a worker in-process
    Given the leftover probe reports the claude pool is spare
    When the SDK spot trigger runs
    Then the agent SDK is called with permissions bypassed
    And the run is capped by a turn ceiling
    And the SDK worker prompt contains the Claude spot worker skill
    And the SDK worker prompt leads with an instruction to begin
    And no lock remains for the claude pool

  Scenario: A pool already running a spot job is not dispatched twice
    Given the leftover probe reports the claude pool is spare
    And the claude pool is already locked by another agent
    When the SDK spot trigger runs
    Then the agent SDK is not called

  Scenario: A failing agent still releases the pool
    Given the leftover probe reports the claude pool is spare
    And the agent SDK will raise an error
    And the worker has claimed a Kanbus chore
    When the SDK spot trigger runs
    Then no lock remains for the claude pool
    And the claimed Kanbus chore is reopened

  Scenario: An on-demand hold stops the run between messages
    Given the leftover probe reports the claude pool is spare
    And the agent SDK will keep streaming messages
    And the worker has claimed a Kanbus chore
    When the SDK spot trigger runs and the pool is held
    Then the run stops before the agent finishes
    And the lock for the claude pool remains HELD
    And the claimed Kanbus chore is reopened
